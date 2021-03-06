#DayOne to Ghost export tool

This tool will create all the files you'll need to import your DayOne Journal entries into Ghost.

###Dependencies

```
brew install pandoc
pip install pypandoc
```


###Usage

```
$ python dayoneToGhost.py <path to your Journal.dayone>
```

This will create an `dayone_export_<date>.json` file and a `content` directory which contains all your DayOne Photos. All you need to do is to import the `dayone_export_<date>.json` file and copy the `content` directory into your Ghost installation directory.

**Things that will be exported**

* entry text
* creation Date
* images (as post image)
* tags
* stars (as featured posts)

**Coming soon**

* tag imported entries with a custom tag
* use external images (to support also hosted ghost blogs)
* allow more command arguments

**Currently Missing**

* Wheather information
* Location information

This are both things the Ghost data model doesn't support. Maybe I can fill this gap with the upcoming Ghost Apps... (or one of you clever guys have an idea ;) )!

**Big thanks to [José Padilla](https://github.com/jpadilla) as my tool is based on his [tumblr-to-ghost](https://github.com/jpadilla/tumblr-to-ghost) export tool.**
