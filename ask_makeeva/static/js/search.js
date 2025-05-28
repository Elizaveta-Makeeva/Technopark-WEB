$(document).ready(function() {
    const searchInput = $('#search-input');
    const searchResults = $('#search-results');
    let searchTimeout;

    searchInput.on('input', function() {
        clearTimeout(searchTimeout);
        const query = $(this).val().trim();

        if (query.length < 2) {
            searchResults.hide().empty();
            return;
        }

        searchTimeout = setTimeout(() => {
            $.get('/search/', { q: query }, function(data) {
                if (data.results.length > 0) {
                    searchResults.empty();
                    data.results.forEach(result => {
                        searchResults.append(`
                            <a class="dropdown-item" href="${result.url}">
                                <div class="fw-bold">${result.title}</div>
                                <small class="text-muted">${result.text}</small>
                            </a>
                        `);
                    });
                    searchResults.show();
                } else {
                    searchResults.hide().empty();
                }
            });
        }, 300);
    });


    $(document).on('click', function(e) {
        if (!$(e.target).closest('#search-form').length) {
            searchResults.hide();
        }
    });

    $('#search-form').on('submit', function(e) {
        e.preventDefault();
        const query = searchInput.val().trim();
        if (query) {
            window.location.href = `/search/?q=${encodeURIComponent(query)}`;
        }
    });
});