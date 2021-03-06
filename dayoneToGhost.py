import os
import sys
import shutil
import subprocess
import plistlib
import glob
import json
import time
import pypandoc as pandoc


def date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj

class DayoneToGhost(object):
    def __init__(self):

        self.used_tags = []
        self.ghost_tags = []
        self.posts_tags = []

        pathToJournalDayone = sys.argv[1]

        self.get_posts(pathToJournalDayone)


    def get_posts(self, pathToJournalDayone):

        if os.path.isdir(pathToJournalDayone):
            print "DayOne path: " + pathToJournalDayone

            f = open('dayone_export.' + time.strftime("%Y-%m-%d") + '.json', 'w')
            f.write(self.create_ghost_export(pathToJournalDayone))
        else:
            print "Path is not a directory"

    def create_ghost_export(self, pathToJournalDayone):

        entries_dir = pathToJournalDayone + "/entries/"
        photos_dir  = pathToJournalDayone + "/photos/"

        ghost_posts = []
        dayone_tags = []
        post_id = 0
        image_count = 0

        entries = glob.glob(entries_dir + "*.doentry")

        for entry in entries:
            post_id += 1
            dayone_tags = []

            pl = plistlib.readPlist(entry)

            timestamp = json.dumps(pl['Creation Date'], default=date_handler)
            timestamp = time.strptime(timestamp, "\"%Y-%m-%dT%H:%M:%S\"")

            # Find corresponding image
            image_name = entry[len(entries_dir):len(entry)-7] + "jpg"
            ghost_img = "None"

            #If an photo exists
            #   - create ghost content directory structure
            #   - copy photo to ghost content directory structure
            #   - create new path to photo in ghost content directory structure
            if os.path.isfile(photos_dir + image_name):

                # ghost content directory structure
                ghost_img_dir = time.strftime("content/images/%Y/%m/", timestamp)
                # Creates content directory with structure: content/images/<year>/<month>/
                subprocess.call(['mkdir','-p', ghost_img_dir]) # create directories

                # copy photo from DayOne photos directory to ghost_img_dir
                shutil.copy(photos_dir + image_name, ghost_img_dir)

                # new path to Photo
                ghost_img = "/" + ghost_img_dir + image_name
                image_count += 1

            markdown = pl["Entry Text"]
            markdown.encode('utf-8', 'xmlcharrefreplace')

            try:
                html = pandoc.convert(markdown, 'html', format='md')
            except:
                print "Issue with following entry:"
                print markdown


            # t.b.d
            try:
                pl["Tags"]
            except KeyError:
                pl["Tags"] = []

            dayone_tags.extend(pl["Tags"])
            post_tags = self.create_tags(set(dayone_tags))

            # the post title is set to the posts date
            # a better/alternative solution wanted!
            title = time.strftime("%d. %b %Y", timestamp)
            slug = time.strftime("%Y-%m-%dT%H:%M:%S", timestamp)

            # Convert timestamp to string
            timestamp = time.strftime("%Y-%m-%dT%H:%M:%S", timestamp)

            # Test if entry is starred in order to make it an featured post
            featured = 0

            try:
                pl["Starred"]
                if not pl["Starred"]:
                    featured = 0
                else:
                    featured = 1
            except KeyError:
                pl["Starred"] = []

            temp_post = {
                "id": post_id,
                "title": title,
                "slug": slug,
                "markdown": markdown,
                "html": html,
                "image": ghost_img,
                "featured": featured,
                "page": 0,
                "status": "published",
                "language": "en_US",
                "meta_title": "None",
                "meta_description": "None",
                "author_id": 1,
                "created_at": timestamp,
                "created_by": 1,
                "updated_at": timestamp,
                "updated_by": 1,
                "published_at": timestamp,
                "published_by": 1
            }

            ghost_posts.append(temp_post)

            self.create_post_tags(temp_post, post_tags)

        export_object = {
            "meta": {
                "exported_on": int(time.time()) * 1000,
                "version": "000"
            },
            "data": {
                "posts": ghost_posts,
                "tags": self.ghost_tags,
                "posts_tags": self.posts_tags
            }
        }

        print "Imported " + str(post_id) + " journal entries and " + str(image_count) + " photos."
        return json.dumps(export_object)


    def create_tags(self, dayone_tags):
        post_tags =[]
        if len(self.ghost_tags) > 0:
            tag_id = self.ghost_tags[-1]['id']
        else:
            tag_id = 0

        for tag in dayone_tags:
            tag_slug = '-'.join(tag.lower().strip(',').split(' '))

            # if tag is not already known, create it and add it to
            # already known tags,ghost_tags ans current posts tags
            # else just add it to current posts tags
            if tag_slug not in self.used_tags:
                now = int(time.time()) * 1000
                tag_id += 1

                temp_tag = {
                    "id": tag_id,
                    "name": tag.title(),
                    "slug": tag_slug,
                    "description": "None",
                    "parent_id": "0",
                    "meta_title": "None",
                    "meta_description": "None",
                    "created_at": now,
                    "created_by": 1,
                    "updated_at": now,
                    "updated_by": 1
                }
                post_tags.append(temp_tag)
                self.ghost_tags.append(temp_tag)
                self.used_tags.append(tag_slug)
            else:
                # get the whole dataset of the already known tag
                # and add it to current posts tags
                for l in self.ghost_tags:
                    if l['slug'] ==  tag_slug:
                        post_tags.append(l)

        return post_tags

    def create_post_tags(self, post, tags):

        for tag in tags:
            self.posts_tags.append({
                "post_id": post["id"],
                "tag_id": tag["id"]
            })


DayoneToGhost()