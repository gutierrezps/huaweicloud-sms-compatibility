# Huawei Cloud SMS compatibility checker

Huawei Cloud's Server Migration Service (SMS) compatibility checker, based
on <https://support.huaweicloud.com/intl/en-us/sms_faq/sms_faq_0007.html>.

## Setup

```plain
conda create -n hwcloud-sms python=3.9 -y
conda activate hwcloud-sms
pip install -r requirements.txt
```

## Usage

1. Run `get-os-list.py` to fetch the latest list of compatible operating systems
   (HTML will be saved to `data/cache.html` and OS list will be saved to `data/os-list.json`);
