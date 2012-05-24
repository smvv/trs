(function ($) {
    var QUEUE = MathJax.Hub.queue;  // shorthand for the queue
    var math = null; // the element jax for the math output

    var trigger_update = true;
    var input_textarea = $('#MathInput');

    // Set the requested query as input value if a query string is given.
    if (location.search.substr(0, 3) == '?q=')
        input_textarea.val(decodeURIComponent(location.search.substr(3)));

    input_textarea.change(function(){ trigger_update = true; })
        .keyup(function(){ trigger_update = true; });

    $('#input').click(function(){
        input_textarea.focus();
    });

    // Get the element jax when MathJax has produced it.
    QUEUE.Push(function() {
        // The onchange event handler that typesets the math entered
        // by the user.  Hide the box, then typeset, then show it again
        // so we don't see a flash as the math is cleared and replaced.
        var update_math = function(tex) {
            var parts = tex.split('\n');

            var math_container = $('#math'),
                math_lines = math_container.find('div.box script');

            // Select all mathjax instances which are inside a div.box element
            var mathjax_instances = [];
            var all_instances = MathJax.Hub.getAllJax('math');

            for (var i = 0; i < all_instances.length; i++) {
                var elem = all_instances[i];

                if ($('#' + elem.inputID).parent().hasClass('box'))
                    mathjax_instances.push(elem);
            }

            var real_lines = 0,
                updated_line = -1;

            for (var p = 0; p < parts.length; p++) {
                if (!parts[p])
                    continue;

                // Check if we want to update an existing line or append the
                // line.
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

            QUEUE.Push(function() {
                // Remove out-dated mathematical lines.
                for (var p = real_lines; p < math_lines.length; p++)
                    $(math_lines[p].parentNode).remove();

                // Remove old hints, given that at least one line is updated.
                // Iterate over the DOM nodes until the updated line is found,
                // and remove all following hint nodes.  Note that if there is
                // no line updated, all hints not directly following the last
                // line are removed.
                var elems = $('#math div');

                if(updated_line == -1)
                    updated_line = real_lines;

                for(var i = 0, lines = 0, hints = 0; i < elems.length; i++) {
                    var elem = $(elems[i]);

                    if (lines > updated_line || hints >= updated_line) {
                        if (elem.hasClass('hint'))
                            elem.remove();
                    } else if (elem.hasClass('hint'))
                        hints++;
                    else if (elem.hasClass('box'))
                        lines++;
                }
            });
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
