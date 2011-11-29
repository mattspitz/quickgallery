import optparse
import os
import Queue
import sys

from mako.template import Template
from PIL import ExifTags, Image

def parse_args():
    parser = optparse.OptionParser()
    parser.add_option("-t", "--thumbnail_width", default=200, action="store", help="width of thumbnails displayed on each page")
    parser.add_option("-g", "--gallery_dest", default="gallery", action="store", help="folder name for where the gallery should be generated")

    (options, args) = parser.parse_args()

    argsdct = options.__dict__.copy()
    try:
        argsdct["srcdir"] = args[0]
    except Exception:
        parser.error("Must provide source directory.")
        sys.exit(1)

    return argsdct

class Job(object):
    def __init__(self, srcdir, targetdir, thumb_width, queue):
        self.srcdir = srcdir
        self.targetdir = targetdir
        self.thumb_width = thumb_width
        self.queue = queue

    def parse_srcdir(self):
        subdirs, image_files = [], []

        image_extensions = ["jpg", "png", "gif", "jpeg"]

        for path in os.listdir(self.srcdir):
            path = os.path.join(self.srcdir, path)
            if os.path.isdir(path):
                subdirs.append(path)
            # full path -> extension
            elif os.path.splitext(os.path.basename(path))[1][1:].lower() in image_extensions:
                image_files.append(path)

        return subdirs, image_files

    def generate_index(self, indexfn, subdirectories, image_files):
        template = Template(filename="index.mako")
        image_fns = []
        for image_fn in sorted(image_files):
            basename = os.path.basename(image_fn)
            image_fns.append( (basename,
                               os.path.join("_thumbnails", basename),
                               os.path.join("_originals", basename)) )

        template_args = {"thisdir": os.path.basename(self.srcdir) or os.path.basename(os.path.dirname(self.srcdir)),
                         "subdirectories": sorted([ os.path.basename(d) for d in subdirectories ]),
                         "image_fns": image_fns,
                         "thumb_width": self.thumb_width}

        output_f = open(indexfn, "w")
        output_f.write( template.render(**template_args) )
        output_f.close()

    def run(self):
        print self.srcdir

        subdirectories, image_files = self.parse_srcdir()

        # make target directory
        os.mkdir(self.targetdir)

        if image_files:
            # link the original directory
            os.symlink(os.path.abspath(self.srcdir), os.path.join(self.targetdir, "_originals"))

            # generate thumbnails
            thumbnail_dir = os.path.join(self.targetdir, "_thumbnails")
            os.mkdir(thumbnail_dir)
            for ifile in image_files:
                im = Image.open(ifile)
                try:
                    exif=dict((ExifTags.TAGS.get(k), v) for k, v in im._getexif().items())
                    rotation = {3: 180,
                                6: 270,
                                8: 90}.get(exif['Orientation'], 0)
                    if rotation:
                        im = im.rotate(rotation, expand=True)
                    im.thumbnail((self.thumb_width, self.thumb_width), Image.ANTIALIAS)
                except Exception:
                    print "\t...error creating thumbnail for", ifile

                im.save(os.path.join(thumbnail_dir, os.path.basename(ifile)))

        # generate index file
        self.generate_index(os.path.join(self.targetdir, "index.html"), subdirectories, image_files)

        # generate HTML to render it
        for directory in subdirectories:
            targetdir = os.path.join(self.targetdir, os.path.basename(directory))
            self.queue.put(Job(directory,
                               targetdir,
                               self.thumb_width,
                               self.queue))

def process_queue(queue):
    while queue.qsize():
        queue.get().run()

def main():
    argsdct = parse_args()

    queue = Queue.Queue()
    queue.put(Job(argsdct["srcdir"],
                  argsdct["gallery_dest"],
                  argsdct["thumbnail_width"],
                  queue))

    process_queue(queue)

if __name__ == "__main__":
    main()
