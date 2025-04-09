from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


def paginate(objects_list, request, per_page=10, pages_around=3):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    page_obj.pages_to_show = get_pages_to_show(
        current_page=page_obj.number,
        total_pages=paginator.num_pages,
        pages_around=pages_around
    )

    return page_obj


def get_pages_to_show(current_page, total_pages, pages_around=3):
    pages = {1, total_pages}
    start = max(1, current_page - pages_around)
    end = min(total_pages, current_page + pages_around)
    pages.update(range(start, end + 1))

    sorted_pages = sorted(pages)
    result = []

    for i, page in enumerate(sorted_pages):
        if i > 0 and page - sorted_pages[i - 1] > 1:
            result.append(None)
        result.append(page)

    return result