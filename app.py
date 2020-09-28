import streamlit as st
from PIL import Image
import os, random
import base64
import fire
import json
import os
import numpy as np
import tensorflow as tf
import awesome_streamlit as ast
import gpt.src.encoder as encoder
import gpt.src.model as model
import gpt.src.sample as sample
import pages.gan
import pages.home
import pages.text

def main():
    """Main Function of the App"""
    PAGES = {
        'Home': pages.home,
        # 'Home': home_app(),
        'GAN': pages.gan,
        # 'GPT-2': interact_model()
        'GPT-2': pages.text
    }
    st.sidebar.title('Navigation')
    selection = st.sidebar.radio("Select Your Page", list(PAGES.keys()))
    page = PAGES[selection]
    with st.spinner(f"Loading {selection} ..."):
        ast.shared.components.write_page(page)

    st.sidebar.title("About")
    st.sidebar.info(
        """
        This app is maintained by Aidan Curley. You can learn more about me and future projects on
        [LinkedIn](https://www.linkedin.com/in/aidancurley/).
        """
    )

if __name__ == "__main__":
    main()
    # if st.button('GPT-2'):
    #     fire.Fire(interact_model)