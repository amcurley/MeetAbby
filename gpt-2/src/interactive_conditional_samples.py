#!/usr/bin/env python3

import fire
import json
import os
import numpy as np
import tensorflow as tf
import send_tweet
import model, sample, encoder

tweets = """

1: This restaurant was horrible.
2: Where did you eat?

1: This food was disgusting.
2: Where did you eat?

1: What is your favorite food?
2: Pizza

1: I love pizza.
2: Same I love pizza.

1: Seafood is gross.
2: I hate seafood.

1: What should I get to eat?
2: I recommend pizza.

1: I am unsure what to eat.
2: Get pizza!

1: What should we do for dinner.
2: Get Italian food.

1: I love food.
2: What type of food?

1: I can't wait to eat.
2: I am so hungry.

"""

def interact_model(
    model_name='774M',
    seed=None,
    nsamples=1,
    batch_size=1,
    length=40,
    temperature=1,
    top_k=0,
    top_p=1,
    models_dir='models',
):
    """
    Interactively run the model
    :model_name=124M : String, which model to use
    :seed=None : Integer seed for random number generators, fix seed to reproduce
     results
    :nsamples=1 : Number of samples to return total
    :batch_size=1 : Number of batches (only affects speed/memory).  Must divide nsamples.
    :length=None : Number of tokens in generated text, if None (default), is
     determined by model hyperparameters
    :temperature=1 : Float value controlling randomness in boltzmann
     distribution. Lower temperature results in less random completions. As the
     temperature approaches zero, the model will become deterministic and
     repetitive. Higher temperature results in more random completions.
    :top_k=0 : Integer value controlling diversity. 1 means only 1 word is
     considered for each step (token), resulting in deterministic completions,
     while 40 means 40 words are considered at each step. 0 (default) is a
     special setting meaning no restrictions. 40 generally is a good value.
     :models_dir : path to parent folder containing model subfolders
     (i.e. contains the <model_name> folder)
    """
    models_dir = os.path.expanduser(os.path.expandvars(models_dir))
    if batch_size is None:
        batch_size = 1
    assert nsamples % batch_size == 0

    enc = encoder.get_encoder(model_name, models_dir)
    hparams = model.default_hparams()
    with open(os.path.join(models_dir, model_name, 'hparams.json')) as f:
        hparams.override_from_dict(json.load(f))

    if length is None:
        length = hparams.n_ctx // 2
    elif length > hparams.n_ctx:
        raise ValueError("Can't get samples longer than window size: %s" % hparams.n_ctx)

    with tf.Session(graph=tf.Graph()) as sess:
        context = tf.placeholder(tf.int32, [batch_size, None])
        np.random.seed(seed)
        tf.set_random_seed(seed)
        # Tokens created from the sample
        output = sample.sample_sequence(
            hparams=hparams, length=length,
            context=context,
            batch_size=batch_size,
            temperature=temperature, top_k=top_k, top_p=top_p
        )

        saver = tf.train.Saver()
        ckpt = tf.train.latest_checkpoint(os.path.join(models_dir, model_name))
        saver.restore(sess, ckpt)

        while True:
            # Twitter input will go here
            raw_text = input("Tweet >>> ")
            while not raw_text:
                # Twitter input will go here
                print('Prompt should not be empty!')
                # Twitter input will go here
                raw_text = input("Tweet >>> ")
            raw_text = tweets + "1: " + raw_text + "\n2: "
            context_tokens = enc.encode(raw_text)
            generated = 0
            for _ in range(nsamples // batch_size):
                out = sess.run(output, feed_dict={
                    context: [context_tokens for _ in range(batch_size)]
                })[:, len(context_tokens):]
                for i in range(batch_size):
                    generated += 1
                    text = enc.decode(out[i])

                    # Response cleaning
                    text = text.replace('1: ', '')
                    text = text.replace('2: ', '')
                    text = text.split("\n")

                    # This is where my twitter bot script will run!
                    send_tweet.update_status(text[2])
                    print("=" * 40 + " SAMPLE " + str(generated) + " " + "=" * 40)
                    print(text)
            print("=" * 80)

if __name__ == '__main__':
    fire.Fire(interact_model)
