
from itemadapter import ItemAdapter
from myproana.models import db_connect, create_table, Author, Thread, Subforum, Post, Authorinfo
import sqlalchemy.orm as orm
from myproana.items import ThreadItem, PostItem
from sqlalchemy import exc


class MyproanaPipeline:
    def __init__(self):
        """
        Initializes database connection and sessionmaker
        Creates tables
        """
        engine = db_connect()
        create_table(engine)
        self.Session = orm.sessionmaker(bind=engine)

    def process_item(self, item, spider):
        """Save quotes in the database
        This method is called for every item pipeline component
        """

        if isinstance(item, ThreadItem):
            self.process_thread(item, spider)
        if isinstance(item, PostItem):
            self.process_post(item, spider)

    def process_thread(self, item, spider):
        session = self.Session()
        thread = Thread()
        author = Author()
        subforum = Subforum()

        author.name = item["authorname"]
        thread.title = item["threadtitle"]
        thread.startdate = item["startdate"]
        thread.url = item["url"]
        subforum.name = item["subforumname"]

        exist_author = session.query(Author).filter_by(name=author.name).first()
        if exist_author is not None:  # the current author exists
            thread.author_id = exist_author.id
        else:
            thread.author = author

        exist_subforum = session.query(Subforum).filter_by(name=subforum.name).first()
        if exist_subforum is not None:  # the current subforum exists
            thread.subforum_id = exist_subforum.id
        else:
            thread.subforum = subforum

        try:
            session.add(thread)
            session.flush()
            session.commit()
        except:
            session.rollback()
            raise

        finally:
            session.close()
        session.close()

        return item

    def process_post(self, item, spider):
        session = self.Session()
        thread = Thread()
        author = Author()
        post = Post()
        authorinfo = Authorinfo()

        post.content = item["postcontent"]
        post.date = item["date"]
        post.sign = item["authorsign"]
        post.noposts = item["noposts"]
        author.name = item["authorname"]
        thread.title = item["threadtitle"]
        authorinfo.type = item["authortype"]

        authorinfo.author = author

        exist_author = session.query(Author).filter_by(name=author.name).first()
        if exist_author is not None:  # the current author exists
            post.author_id = exist_author.id
        else:
            post.author = author

        exist_thread = session.query(Thread).filter_by(title=thread.title).first()
        post.thread_id = exist_thread.id


        try:
            session.add(post)
            session.commit()
        except:
            session.rollback()
            raise

        finally:
            session.close()
        session.close()

        return item

