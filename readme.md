# SepSpider: Spider for [UCAS SEP platform](http://sep.ucas.ac.cn/)
SepSpider is a spider based on scrapy and selenium for automatically crawling and updating UCAS class resources. It's also suitable for server deployment. 
## Requirements
1. Linux (Ubuntu recommended)
2. Python3
   - scrapy
   - pillow
   - selenium
3. Firefox

## Usage
1. Set up account info at `sep_spider/custom_setting.py`.

```python custom_setting.py
# sep user info
SEP_USER = 'your sep account (email)'
SEP_PASSWD = 'your password'

# The spider use Yundama for QR Code recognition.
# If you don't have one, create an User account (NOT a Developer one) at:
# http://www.yundama.com/
# and add some credits to it.

# yundama user info
YDM_INFO = {
    'username': 'yundama username',
    'password': 'yundama password',
    'appid': 8741,
    'appkey': 'c2f7b93e58d4721079da3822c7aad5d4'
}

# where to store you file
CUSTOM_FILES_STORE = 'sep/'

# touch reload path used by listener
RELOAD_PATH = './reload'
```

Yundama account is needed for QR Code recognition. Create an **User (NOT Developer)** account at http://www.yundama.com/ and add a little credits to it. 5 RMB is enough for a year's use.

2. run spider
```bash
cd sep_spider
scrapy crawl sep_spider
```
The default location to store files is `./sep`. It can be customized in `sep_spider/custom_setting.py`.

### Listener usage
For server deployment, you can run `listener.py` to listen to the changes of `reload` file as the signal of recrawling. Recrawling will only download non-existing files. **It won't modify existing files**.

1. Set up your environment and account info (see above)
2. Run `listener.py`
```bash
python listener.py
```
3. Everytime you modify the `reload` file, the spider will recrawl the resources. The location of reload file is customizable in `sep_spider/custom_setting.py`.
```bash
touch reload
```
