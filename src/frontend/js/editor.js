(function ($) {
    var QUEUE = MathJax.Hub.queue;  // shorthand for the queue
    var math = null; // the element jax for the math output

    // Hide and show the box (so it doesn't flicker as much)
    //var hide_box = function () {box.style.visibility = 'hidden'}
    //var show_box = function () {box.style.visibility = 'visible'}
    var trigger_update = true;

    //// Initialise codemirror environment
    //var input_textarea = document.getElementById('MathInput'),
    //    input_box = CodeMirror.fromTextArea(input_textarea, {
    //        value: '',
    //        mode:  'r',
    //        matchBrackets: true,
    //        onChange: function(f) { trigger_update = true; }
    //    });

    var input_textarea = $('#MathInput');

    input_textarea.change(function(){ trigger_update = true; })
        .keyup(function(){ trigger_update = true; });

    $('#input').click(function(){
        //input_box.focus();
        input_textarea.focus();
    });

    // Get the element jax when MathJax has produced it.
    QUEUE.Push(function() {
        //math = MathJax.Hub.getAllJax('MathOutput')[0];
        //box = document.getElementById('box');
        //show_box();

        // The onchange event handler that typesets the math entered
        // by the user.  Hide the box, then typeset, then show it again
        // so we don't see a flash as the math is cleared and replaced.
        var update_math = function(tex) {
            var parts = tex.split('\n');

            var math_container = $('#math'),
                math_lines = math_container.find('div.box script'),
                mathjax_instances = MathJax.Hub.getAllJax('math');

            var real_lines = 0,
                updated_line = -1;

            for (var p = 0; p < parts.length; p++) {
                if (!parts[p])
                    continue;

                // TODO: Mark updated line as "pending" (e.g. remove "wrong"
                // and "good" class names from element).

                if (real_lines < math_lines.length) {
                    var elem = mathjax_instances[real_lines];

                    // Update the line when the input is modified.
                    if (elem.originalText != parts[p]) {
                        updated_line = real_lines;
                        QUEUE.Push(['Text', elem, parts[p]]);
                    }

                    if (updated_line > -1) {
                        // Remove the out-of-date status information. This will
                        // be done from now on for all remaining lines, whether
                        // they are up-to-date or not.
                        $(math_lines[real_lines]).parent()
                            .removeClass('wrong').removeClass('correct');
                    }
                } else {
                    var line = '`' + parts[p] + '`',
                        elem = $('<div class="box"/>').text(line);

                    math_container.append(elem);

                    QUEUE.Push(['Typeset', MathJax.Hub, elem[0]]);
                }

                real_lines++;
            }

            // Remove old hints, given that at least one line is updated.
            // Iterate over the DOM nodes until the updated line is found,
            // and remove all following hint nodes.
            var line_count = 0, i = 0, elems = $('#math div');

            if(updated_line == -1)
                updated_line = real_lines + 1;

            for(; i < elems.length; i++) {
                var elem = $(elems[i]);

                if (line_count == updated_line) {
                    if (elem.hasClass('hint'))
                        elem.remove();
                } else if (elem.hasClass('box')) {
                    line_count++;
                }
            }

            QUEUE.Push((function(math_lines, real_lines) {
                return function() {
                    for (var p = real_lines; p < math_lines.length; p++) {
                        $(math_lines[p].parentNode).remove();
                    }
                };
            })(math_lines, real_lines));
        }

        window.update_math = function() {
            if (trigger_update) {
                trigger_update = false;
                update_math(input_textarea.val());
            }
        };

        setInterval(window.update_math, 100);
    });

    var loader = $('#loader');

    window.show_loader = function() {
        loader.show().css('display', 'inline-block');
    };

    window.hide_loader = function() {
        loader.hide();
    };

    window.append_hint = function(hint) {
        $('#math div').last().filter('.hint').remove();

        var elem = $('<div class=hint/>');
        elem.text(hint);
        $('#math').append(elem);
        QUEUE.Push(['Typeset', MathJax.Hub, elem[0]]);
    };

    window.append_input = function(input) {
        input_textarea.val(input_textarea.val() + '\n' + input);
    };

    window.answer_input = function() {
        show_loader();

        // TODO: disable input box and enable it when this ajax request is done
        // (on failure and success).
        $.post('/answer', {data: input_textarea.val()}, function(response) {
            if (!response)
                return;

            if ('steps' in response) {
                for(i = 0; i < response.steps.length; i++) {
                    cur = response.steps[i];

                    if ('step' in cur)
                        window.append_input(cur.step);

                    if('hint' in cur)
                        window.append_hint(cur.hint);

                    trigger_update = true;
                    window.update_math();
                }
            }

            if('hint' in response)
                window.append_hint(response.hint);

            input_textarea.focus();

            hide_loader();
        }, 'json').error(function(e) {
            console.log('error:', e);

            hide_loader();
        });
    };

    window.hint_input = function() {
        show_loader();

        // TODO: disable input box and enable it when this ajax request is done
        // (on failure and success).
        $.post('/hint', {data: input_textarea.val()}, function(response) {
            if (!response)
                return;

            window.append_hint(response.hint);

            input_textarea.focus();

            hide_loader();
        }, 'json').error(function(e) {
            console.log('error:', e);

            hide_loader();
        });
    };

    window.step_input = function() {
        show_loader();

        // TODO: disable input box and enable it when this ajax request is done
        // (on failure and success).
        $.post('/step', {data: input_textarea.val()}, function(response) {
            if (!response)
                return;

            console.log(response);

            if ('step' in response) {
                window.append_input(response.step);
                trigger_update = true;
            }

            if('hint' in response)
                window.append_hint(response.hint);

            input_textarea.focus();

            hide_loader();
        }, 'json').error(function(e) {
            console.log('error:', e);

            hide_loader();
        });
    };

    window.validate_input = function() {
        show_loader();

        // TODO: disable input box and enable it when this ajax request is done
        // (on failure and success).
        $.post('/validate', {data: input_textarea.val()}, function(response) {
            if (!response)
                return;

            var math_container = $('#math'),
                math_lines = math_container.find('div.box');

            var i = 0;

            // Mark every line as correct (and remove previous class names).
            for(; i < math_lines.length && i <= response.validated; i++)
                $(math_lines[i]).removeClass('wrong').addClass('correct');

            if (i < math_lines.length) {
                // Mark the current line as wrong.
                $(math_lines[i]).removeClass('correct').addClass('wrong');

                // Remove the status indicator from the remaining lines.
                for(i += 1; i < math_lines.length; i++)
                    $(math_lines[i]).removeClass('correct')
                        .removeClass('wrong');
            }

            hide_loader();
        }, 'json').error(function(e) {
            console.log('error:', e);

            hide_loader();
        });
    };

    window.clear_input = function() {
        input_textarea.val('');
        $('#math .box,#math .hint').remove();
        trigger_update = true;
        hide_loader();
    };
})(jQuery);
