from flask import Blueprint, render_template
from flask import request
from models.models import SearchIndexModel
from sqlalchemy import or_

bp = Blueprint("search", __name__)

@bp.route("/search")
def search():
    query = request.args.get("search-content").strip()  

    if not query:
        return render_template("search-results.html", results=[])
    results = SearchIndexModel.query.filter(
    SearchIndexModel.search_content.match(query)
    ).filter_by(
    is_approved=True
    ).all()
    
    if not results:
        like_pattern = f"%{query}%"
        results = SearchIndexModel.query.filter(
            SearchIndexModel.is_approved == True,
            or_(
                SearchIndexModel.search_content.like(like_pattern),
                SearchIndexModel.title.like(like_pattern),
                SearchIndexModel.description.like(like_pattern)
            )
        ).all()
    return render_template("search-results.html", results=results, query=query)