FROM scrapinghub/scrapinghub-stack-scrapy:2.0
ENV stage=prod
LABEL group=spider
WORKDIR /skystocks
COPY requirements ./
RUN pip install -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com -r requirements
ADD . .
VOLUME ["/var/log/scrapy"]
ENTRYPOINT ["scrapy", "crawl", "history_stocks"]
