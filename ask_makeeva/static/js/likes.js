function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function updateLikeButtons(buttons, userVote) {
    buttons.removeClass('btn-success btn-danger').addClass('btn-outline-success btn-outline-danger');
    if (userVote === 1) {
        buttons.filter('[data-value="1"]').removeClass('btn-outline-success').addClass('btn-success');
        buttons.filter('[data-value="-1"]').addClass('btn-outline-danger');
    } else if (userVote === -1) {
        buttons.filter('[data-value="-1"]').removeClass('btn-outline-danger').addClass('btn-danger');
        buttons.filter('[data-value="1"]').addClass('btn-outline-success');
    }
}

function handleQuestionLike() {
    const btn = $(this);
    const questionId = btn.data('question-id');
    const value = btn.data('value');
    const csrftoken = getCookie('csrftoken');

    $.ajax({
        url: '/question/like/',
        type: 'POST',
        data: {
            'question_id': questionId,
            'value': value,
            'csrfmiddlewaretoken': csrftoken
        },
        dataType: 'json',
        beforeSend: function() {
            btn.prop('disabled', true);
        },
        success: function(data) {
            if (data.status === 'ok') {
                $(`.question-rating[data-question-id="${questionId}"]`).val(data.rating);
                $('#question-rating').val(data.rating);
                const allButtons = $(`.like-btn[data-question-id="${questionId}"]`);
                updateLikeButtons(allButtons, data.user_vote);
            } else {
                alert(data.message || 'Error occurred');
            }
        },
        error: function(xhr) {
            alert('Server error occurred');
        },
        complete: function() {
            btn.prop('disabled', false);
        }
    });
}

function handleAnswerLike() {
    const btn = $(this);
    const answerId = btn.data('answer-id');
    const value = btn.data('value');
    const ratingElement = $(`#answer-${answerId} .answer-rating`);
    const csrftoken = getCookie('csrftoken');

    $.ajax({
        url: '/answer/like/',
        type: 'POST',
        data: {
            'answer_id': answerId,
            'value': value,
            'csrfmiddlewaretoken': csrftoken
        },
        dataType: 'json',
        beforeSend: function() {
            btn.prop('disabled', true);
        },
        success: function(data) {
            if (data.status === 'ok') {
                ratingElement.val(data.rating);
                const allButtons = $(`.answer-like-btn[data-answer-id="${answerId}"]`);
                updateLikeButtons(allButtons, data.user_vote);
            } else {
                alert(data.message || 'Error occurred');
            }
        },
        error: function(xhr) {
            alert('Server error occurred');
        },
        complete: function() {
            btn.prop('disabled', false);
        }
    });
}

$(document).ready(function() {
    $('.like-btn').each(function() {
        const btn = $(this);
        if (btn.hasClass('active')) {
            const value = btn.data('value');
            if (value === 1) {
                btn.removeClass('btn-outline-success').addClass('btn-success');
            } else if (value === -1) {
                btn.removeClass('btn-outline-danger').addClass('btn-danger');
            }
        }
    });

    $('.answer-like-btn').each(function() {
        const btn = $(this);
        if (btn.hasClass('active')) {
            const value = btn.data('value');
            if (value === 1) {
                btn.removeClass('btn-outline-success').addClass('btn-success');
            } else if (value === -1) {
                btn.removeClass('btn-outline-danger').addClass('btn-danger');
            }
        }
    });

    $(document).on('click', '.like-btn', handleQuestionLike);
    $(document).on('click', '.answer-like-btn', handleAnswerLike);
});