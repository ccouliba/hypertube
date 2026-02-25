"""Utility functions for search operations"""

def deduplicate_by_title(results: list[dict]) -> list[dict]:
    """Remove duplicate results based on title (case-insensitive)"""
    unique_results: dict = {}
    for result in results:
        title_key = result["title"].lower()
        if title_key not in unique_results:
            unique_results[title_key] = result
    return list(unique_results.values())


def sort_results(
        results: list[dict],
        sort_by: str,
        order: str
    ) -> list[dict]:
    """Sort results by specified criteria"""
    reverse: bool = (order.lower() == "desc")
    sort_keys: dict[str, callable] = {
        "download_count": lambda x: x.get("download_count") or 0,
        "seeds": lambda x:
            sum(
                t.get("seeds") 
                or 0 for t in x.get("torrents", [])
            ),
        "peers": lambda x:
            sum(
                t.get("peers") 
                or 0 for t in x.get("torrents", [])
            ),
        "rating": lambda x: x.get("rating") or 0,
        "year": lambda x: x.get("year") or 0,
        "title": lambda x: x.get("title", "").lower()
    }
    key_func = sort_keys.get(sort_by, sort_keys["rating"])
    results.sort(key=key_func, reverse=reverse)
    return results


def paginate(
        results: list[dict],
        page: int,
        limit: int
    ) -> dict:
    """Paginate results and return metadata"""
    total_results: int = len(results)
    total_pages: int = (total_results + limit - 1) // limit
    start_index: int = (page - 1) * limit
    end_index: int = start_index + limit
    return {
        "results": results[start_index:end_index],
        "page": page,
        "limit": limit,
        "total_results": total_results,
        "total_pages": total_pages
    }
