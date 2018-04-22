import click
import os
import frontmatter
import boto3
import io
import copy
import hashlib


def log(message):
    print(message)


def isTranslatable(fname):
    isPost = fname.endswith(".markdown")
    notTranslated = fname.count(".") == 1
    isTranslatable = isPost and notTranslated
    return isTranslatable


def translate_text(text, src_lang, dst_lang):
    if (not text):
        return ""
    m = hashlib.md5()
    m.update(text.encode('utf-8'))
    digest = m.hexdigest()
    translated_text = ""
    translate = boto3.client('translate')
    response = translate.translate_text(
        Text=text,
        SourceLanguageCode=src_lang,
        TargetLanguageCode=dst_lang
    )
    translated_text = response['TranslatedText']
    print("== " + digest + "[MISS] ==")
    print(text)
    print("---")
    print(translated_text)
    print("====")
    return translated_text


def translate_post(filePath, src_lang, dst_lang):
    root, ext = os.path.splitext(filePath)
    dst_file = root + "." + dst_lang+ext
    if os.path.exists(dst_file):
        dst_file = root + "." + dst_lang+"_"+ext

    dst_path = dst_file
    dst_post = frontmatter.load(filePath)
    dst_post["dst_lang"] = dst_lang
    f = io.open(dst_path, 'wb')
    content = dst_post.content
    translation = ""
    token = ""
    for char in content:
        if (char == "." or char == "\n"):
            translated_text = translate_text(token, src_lang, dst_lang)
            token = ""
            translated_text += char
            translation += translated_text
        else:
            token += char
    if (token):
        translation += translate_text(token, src_lang, dst_lang)
    dst_post.content = translation
    frontmatter.dump(dst_post, f)
    f.close()
    print('\t => %s' % dst_path)


def translate(dirName, fname, src_lang="en", dst_langs=["es"]):
    filePath = os.path.join(dirName, fname)
    log('\t%s' % filePath)
    for dst_lang in dst_langs:
        translate_post(filePath, src_lang, dst_lang)


@click.command()
def main():
    """A part of a TARDIS that allows for the instantaneous translation of most languages spoken or written in the universe."""
    rootDir = '_posts'
    for dirName, subdirList, fileList in os.walk(rootDir):
        for fname in fileList:
            if isTranslatable(fname):
                translate(dirName, fname)


main()
