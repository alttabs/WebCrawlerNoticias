# -*- coding: utf-8 -*-
import scrapy
import scrapy
import re
import json
import ast
import csv
from urllib.parse import quote
from ast import literal_eval

class G1Spider(scrapy.Spider):
    name = 'G1'

    def start_requests(self):
        # news url
        urls = ['https://g1.globo.com/pr/parana/noticia/2019/11/08/juiz-determina-saida-de-lula-da-prisao-apos-decisao-do-stf.ghtml']
        # request for comments on g1
        self.comments_url = 'https://comentarios.globo.com/comentarios/{0}/{1}/{2}/shorturl/{3}/'
        #interates
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        try:
            #comments ID
            content = response.css('#SETTINGS').get()
            # Filter the response
            # The replace('/','@@') is needed for url encode
            external_id = re.search('COMENTARIOS_IDEXTERNO: "(.*)"', content).group(1).replace("/","@@")
            external_id = quote(external_id)
            comments_uri = re.search('COMENTARIOS_URI: \"(.*)\"(,[A-Z])', content).group(1).replace("/","@@")
            comments_uri = quote(comments_uri)
            title = response.css('head > meta:nth-child(68)').get()
            title =  re.search('content=\"(.*)"', title).group(1)
            title = quote(title)
            cannonical_url = quote(response.url.replace("/","@@"))

        except Exception as err:
            print(err)
            exit(1)
        # endpoint returns the number of comments in the page.
        self.comments_url = self.comments_url.format(comments_uri, external_id, cannonical_url, title)+"numero"

        yield response.follow(self.comments_url, self.get_comments)

    def get_comments(self, response):
        ori_body = response.body.decode()

        body = ori_body.split('({')[1].split('})')[0]

        newBody = body.replace('false', 'False').replace('true','True').replace('null','False').replace(':\'',":\"").replace(':\'',":\"").replace(',',"\",").replace(':',":\"")
        newBody = newBody.replace('}\"', "}").replace('\"editoria\":\"',"\"editoria\":").replace("\"uri\":\"","\"uri\":")
        newBody = newBody + "\""
        print ("cheguei aquiAAAAAAAAAAAAAAAAA Body: " + newBody)

        json_acceptable_string = "{" +  newBody + "}"
        d = json.loads(json_acceptable_string)

        number_of_pages = int(d['limitePaginas'])

        if number_of_pages == 0:
            print("Nothing to do here! Exiting...")
            exit(0)
        self.log("Found {} pages".format(number_of_pages))

        #creating CSV File
        with open('wiki.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Comment", "Evaluation"])
        # Request url comments for each page
        for i in range(1,number_of_pages+1):
            self.log("Crawling...")
            # Follow url comments link
            yield response.follow(self.comments_url.replace('numero',"{}.json".format(i)),
            self.do_comments_analysis)

    def do_comments_analysis(self,response):
        #print ("cheguei aquiAAAAAAAAAAAAAAAAA Analysis" + response)

        ori_body = response.body.decode()
        #print ("cheguei aquiAAAAAAAAAAAAAAAAA Body: " + ori_body)
        ori_body = ori_body.split('({')[1].split('})')[0]

        #print ("cheguei aquiAAAAAAAAAAAAAAAAA Analysis" + ori_body)

        jsonObj = eval("{"+ori_body.replace('false', 'False')
        .replace('true','True')
        .replace('null',"False")+"}")

        #print ("cheguei aquiAAAAAAAAAAAAAAAAA Analysis" + jsonObj['itens'])

        #for items in jsonObj['itens']:
            #print(items)

        for i in range(len(jsonObj['itens'])):
            replies = jsonObj['itens'][i]['replies']
            userObj = jsonObj['itens'][i]['Usuario']
            text = jsonObj['itens'][i]['texto']
            print("---------------------------------------------")
            print(text)

            #creating CSV File
            with open('wiki.csv', 'a') as file:
                writer = csv.writer(file)
                writer.writerow([text, ""])
                #file.write([text, ""])

        #for line in response.text.splitlines():
    #        print (line)

        received_file = response.url.split('/')[-1]
        return received_file

        self.log("Received file {}".format(received_file))
        ori_body = response.body.decode()

        jsonObj = self.body_to_json(ori_body)


        # String for save
        word_token = ""
        for i in range(len(jsonObj['itens'])):
            replies = jsonObj['itens'][i]['replies']
            userObj = jsonObj['itens'][i]['Usuario']
            text = jsonObj['itens'][i]['texto']

    def body_to_json(self, body):
        # Convert body response to json

        body = body.split('(')[1].split(')')[0]
