#!/usr/bin/python2
#  -*- coding: utf-8 -*-

import json
import argparse

parser = argparse.ArgumentParser()
parser.description = "Transform a set of json from DNC scenario to an unique " \
                    "and easly understandable file. Can convert this single " \
                     "file "\
                "back to a set a JSON file for DNC scenario"
parser.add_argument('files', type=str, nargs='+')
parser.add_argument('--from', type=str, required=True, choices=('scenario',
                                                                'text'))
parser.add_argument('--to', type=str, required=True, choices=('scenario',
                                                              'text')
                    )

args = vars(parser.parse_args())

#print "{0}".format(args)

OUTPUT = dict()

def scenario_to_text(path, txt):
    with open(path, 'r') as f:
        scenario = json.load(f, encoding='utf-8')
    for line in scenario["text"].split("\n"):
        line = line.split(":")
        if len(line) > 1:
            txt[line[0]] = ":".join(line[1:])
        else:
            continue

if args['from'] == 'scenario' and args['to'] == 'text':
    for path in args['files']:
        OUTPUT[path.split("text_")[1].split(".json")[0]] = dict()
        scenario_to_text(path, OUTPUT[path.split("text_")[1].split(".json")[0]])
    print json.dumps(OUTPUT, sort_keys=True, indent=4, separators
    =(',', ': '), ensure_ascii=False)
elif args['from'] == 'text' and args['to'] == 'scenario':
    with open(args['files'][0], 'r') as f:
        scenario = json.load(f, encoding='utf-8')
    for scene,textes in scenario.items():
        with open("text_{0}.json".format(scene), 'w') as f:
            content = dict()
            content["text"] = ""
            print("=={0}==".format(scene))
            for key,value in textes.items():
                #value = value.replace("\\n", "\\\\n")
                print("{0}:{1}".format(key.encode("utf-8"), value.encode(
                    "utf-8")))
                content["text"] += "{0}:{1}\n".format(key.encode('utf-8'),
                                                       value.encode('utf-8'))
            json.dump(content, f, encoding='utf-8', ensure_ascii=True)

            # f.write("\"\n}")f.write("{\n")
            # f.write("\t\"text\": \"")
            # for key,value in textes.items():
            #
            #     value = value.replace("\\n", "\\\\n")
            #     print("{0}:{1}".format(key.encode("utf-8"), value.encode(
            #         "utf-8")))
            #     f.write("{0}:{1}\\n".format(key.encode("utf-8"), value.encode(
            #         "utf-8")))
            # f.write("\"\n}")



