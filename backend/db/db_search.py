from elasticsearch import Elasticsearch
from sqlalchemy.orm import Session
from db.models import DbUser as User
from db.models import DbPost as Post
from db.models import DbComment as Comment
from elasticsearch.helpers import bulk

es = Elasticsearch([{"host": "localhost", "port": 9200, "scheme": "http"}],
                   headers={"Content-Type": "application/json"})


def create_index_action(index: str, _id: int, source: dict):
    return {
        "_index": index,
        "_id": _id,
        "_source": source
    }


def ensure_index_exists(index_name):
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name)


def index_data_to_es(session: Session, new_data=None):
    actions = []

    if new_data:
        ensure_index_exists(new_data["_index"])
        actions.append(new_data)
    else:
        users = session.query(User).all()
        for user in users:
            actions.append({
                "_index": "users",
                "_id": user.id,
                "_source": {
                    "username": user.username,
                    "email": user.email
                }
            })

        posts = session.query(Post).all()
        for post in posts:
            actions.append({
                "_index": "posts",
                "_id": post.id,
                "_source": {
                    "content": post.caption,
                    "timestamp": post.timestamp.isoformat() if post.timestamp else None,
                    "username": post.user.username
                }
            })

        comments = session.query(Comment).all()
        for comment in comments:
            actions.append({
                "_index": "comments",
                "_id": comment.id,
                "_source": {
                    "content": comment.text,
                    "timestamp": comment.timestamp.isoformat() if comment.timestamp else None
                }
            })

    bulk(es, actions, raise_on_error=True, request_timeout=30)


def search_in_es(query_str: str):
    indices = ["users", "posts", "comments"]
    results = {
        "users": [],
        "posts": [],
        "comments": []
    }
    available_indices = [index for index in indices if es.indices.exists(index=index)]

    search_results = es.search(index=",".join(available_indices), body={
        "query": {
            "multi_match": {
                "query": query_str,
                "fields": ["username", "email", "content"],
                "type": "best_fields"
            }
        }
    })

    for hit in search_results["hits"]["hits"]:
        index = hit["_index"]
        if index == "users":
            results["users"].append(hit["_source"])
        elif index == "posts":
            results["posts"].append(hit["_source"])
        elif index == "comments":
            results["comments"].append(hit["_source"])

    return results
