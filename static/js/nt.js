(function () {
  var input = $('#info');
  var sendButton = $('#send');
  var chat = $('#chat');
  var csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

  function appendMessage(role, content) {
    var message = $('<div>', { class: role });
    $('<div>', { class: 'item', text: content }).appendTo(message);
    chat.append(message);
    chat.scrollTop(chat[0].scrollHeight);
  }

  function sendQuestion() {
    var question = $.trim(input.val());
    if (!question || sendButton.prop('disabled')) {
      return;
    }

    appendMessage('me', question);
    input.val('');
    sendButton.prop('disabled', true).text('发送中…');

    $.ajax({
      url: '/chat/add',
      method: 'POST',
      data: { q: question },
      headers: { 'X-CSRFToken': csrfToken },
    })
      .done(function (answer) {
        appendMessage('robot', $.trim(answer) || '暂未找到相关答案。');
      })
      .fail(function (request) {
        appendMessage('robot', $.trim(request.responseText) || '问答服务暂不可用，请稍后再试。');
      })
      .always(function () {
        sendButton.prop('disabled', false).text('发送');
        input.trigger('focus');
      });
  }

  sendButton.on('click', sendQuestion);
  input.on('keydown', function (event) {
    if (event.key === 'Enter') {
      event.preventDefault();
      sendQuestion();
    }
  });
})();
