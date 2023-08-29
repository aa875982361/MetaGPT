#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/8/17
@Author  : mashenquan
@File    : openai_text_to_image.py
@Desc    : OpenAI Text-to-Image OAS3 api, which provides text-to-image functionality.
"""
import base64
import os
import sys
from pathlib import Path
from typing import List

import aiohttp
import requests
from pydantic import BaseModel

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))  # fix-bug: No module named 'metagpt'
from metagpt.logs import logger


class OpenAIText2Image:
    def __init__(self, openai_api_key):
        """
        :param openai_api_key: OpenAI API key, For more details, checkout: `https://platform.openai.com/account/api-keys`
        """
        self.openai_api_key = openai_api_key if openai_api_key else os.environ.get('OPENAI_API_KEY')

    async def text_2_image(self, text, size_type="1024x1024"):
        """Text to image

        :param text: The text used for image conversion.
        :param size_type: One of ['256x256', '512x512', '1024x1024']
        :return: The image data is returned in Base64 encoding.
        """

        class ImageUrl(BaseModel):
            url: str

        class ImageResult(BaseModel):
            data: List[ImageUrl]
            created: int

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openai_api_key}"
        }
        data = {"prompt": text, "n": 1, "size": size_type}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post("https://api.openai.com/v1/images/generations", headers=headers, json=data) as response:
                    result = ImageResult(** await response.json())
        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred:{e}")
            return ""
        if len(result.data) > 0:
            return await OpenAIText2Image.get_image_data(result.data[0].url)
        return ""

    @staticmethod
    async def get_image_data(url):
        """Fetch image data from a URL and encode it as Base64

        :param url: Image url
        :return: Base64-encoded image data.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()  # 如果是 4xx 或 5xx 响应，会引发异常
                    image_data = await response.read()
            base64_image = base64.b64encode(image_data).decode("utf-8")
            return base64_image

        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred:{e}")
            return ""


# Export
async def oas3_openai_text_to_image(text, size_type: str = "1024x1024", openai_api_key=""):
    """Text to image

    :param text: The text used for image conversion.
    :param openai_api_key: OpenAI API key, For more details, checkout: `https://platform.openai.com/account/api-keys`
    :param size_type: One of ['256x256', '512x512', '1024x1024']
    :return: The image data is returned in Base64 encoding.
    """
    if not text:
        return ""
    if not openai_api_key:
        openai_api_key = os.environ.get("OPENAI_API_KEY")
    return await OpenAIText2Image(openai_api_key).text_2_image(text, size_type=size_type)


if __name__ == "__main__":
    v = oas3_openai_text_to_image("Panda emoji")
    print(v)
