(function($, undefined) {
    // http://stackoverflow.com/questions/1891444/how-can-i-get-cursor-position-in-a-textarea
    $.fn.getCursorPosition = function() {
        var el = $(this).get(0);
        var pos = 0;

        if ('selectionStart' in el) {
            pos = el.selectionStart;
        } else if ('selection' in document) {
            el.focus();
            var Sel = document.selection.createRange();
            var SelLength = document.selection.createRange().text.length;
            Sel.moveStart('character', -el.value.length);
            pos = Sel.text.length - SelLength;
        }

        return pos;
    };

    var QUEUE = MathJax.Hub.queue;  // shorthand for the queue
    var math = null; // the element jax for the math output

    var trigger_update = true;
    var input_textarea = $('#math-input');
    var pretty_print = $('#pretty-print');

    // Set the requested query as input value if a query string is given.
    if (location.search.substr(0, 3) == '?q=')
        input_textarea.val(decodeURIComponent(location.search.substr(3)));

    input_textarea.bind('change keyup click', function() {
        trigger_update = true;
    });

    input_textarea.closest('div').click(function() {
        input_textarea.focus();
    });

    // Put cursor at end of textarea
    var old_val = input_textarea.val();
    input_textarea.val('').focus().val(old_val);

    var STATUS_FAILURE = 0,
        STATUS_NOPROGRESS = 1,
        STATUS_SUCCESS = 2,
        STATUS_ERROR = 3;

    var status_icons = ['thumbs-down', 'thumbs-up', 'thumbs-up', 'remove'];
    var status_labels = ['important', 'warning', 'success', 'important'];
    var status_titles = ['Incorrect', 'No progress', 'Correct', 'Error'];
    var status_messages = [
        'This step is incorrect.',
        'This step leads to the correct answer, but not in a lower number of '
        + 'steps than the previous step.',
        'This step is correct.',
        'An error occurred while validating this step.'
    ];

    function set_status(elem, stat) {
        elem = $(elem);
        elem.find('.label').remove();

        if (stat !== undefined) {
            var label = $('<span class="label label-'
                          + status_labels[stat] + '"/>');
            label.append('<i class="icon-white icon-'
                         + status_icons[stat] + '"/>');
            //label.tooltip({placement: 'left', title: status_messages[stat]});
            label.popover({
                placement: 'left',
                trigger: 'hover',
                title: status_titles[stat],
                content: status_messages[stat]
            });
            elem.append(label);
        }
    }

    function get_current_line() {
        var input = input_textarea.val(),
            caret = input_textarea.getCursorPosition(),
            lines = 0;

        for (var i = 0; i < caret; i++) {
            if (input.charAt(i) == '\n')
                lines++;
        }

        return lines;
    }

    // Get the element jax when MathJax has produced it.
    QUEUE.Push(function() {
        // The onchange event handler that typesets the math entered
        // by the user.  Hide the box, then typeset, then show it again
        // so we don't see a flash as the math is cleared and replaced.
        var update_math = function(tex) {
            var parts = tex.split('\n');
            var math_lines = pretty_print.find('div.box script');

            // Stretch textarea size with number of input lines
            input_textarea.attr('rows', parts.length);

            // Select all mathjax instances which are inside a div.box element
            var mathjax_instances = [];
            var all_instances = MathJax.Hub.getAllJax('pretty-print');

            for (var i = 0; i < all_instances.length; i++) {
                var elem = all_instances[i];

                if ($('#' + elem.inputID).parent().hasClass('box'))
                    mathjax_instances.push(elem);
            }

            var real_lines = 0,
                updated_line = -1,
                current_line = get_current_line();

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

                    elem = $(math_lines[real_lines]).parent();

                    if (updated_line > -1) {
                        // Remove the out-of-date status information. This will
                        // be done from now on for all remaining lines, whether
                        // they are up-to-date or not.
                        set_status(elem);
                    }
                } else {
                    var line = '`' + parts[p] + '`',
                        elem = $('<div class="box"/>').text(line);

                    pretty_print.append(elem);

                    QUEUE.Push(['Typeset', MathJax.Hub, elem[0]]);
                }

                // Highlight current line.
                $(elem).toggleClass('current-line', p == current_line);

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
                var elems = pretty_print.find('div');

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

                // Preprocess input to fix TRS-MathJax incompatibilities.
                var input = input_textarea.val();

                // Make sure that xx is not displayed as a cross.
                input = input.replace(/xx/g, 'x x');

                update_math(input);
            }
        };

        window.update_math();
        setInterval(window.update_math, 100);
    });

    var error = $('#error'),
        loader = $('#loader');

    function report_error(e) {
        var msg = e.error;

        if ('statusText' in e)
            msg = e.status + ' ' + e.statusText;

        error.show().find('.text').text(msg);

        if (console && console.log)
            console.log('error:', e);

        hide_loader();
    }

    function clear_error() {
        error.hide();
    }

    error.find('.close').click(clear_error);

    var pending_request = false;

    function show_loader() {
        pending_request = true;
        loader.css('visibility', 'visible');
    }

    function hide_loader() {
        pending_request = false;
        loader.css('visibility', 'hidden');
    }

    function append_hint(hint) {
        pretty_print.find('div').last().filter('.hint').remove();

        var elem = $('<div class="hint"/>');
        elem.text(hint);
        elem.append('<div class="icon icon-info-sign"/>');
        pretty_print.append(elem);
        QUEUE.Push(['Typeset', MathJax.Hub, elem[0]]);
    }

    function append_input(input) {
        input_textarea.val(input_textarea.val() + '\n' + input);
    }

    $('#btn-clear').click(function() {
        clear_error();
        hide_loader();
        input_textarea.val('').focus();
        trigger_update = true;
        window.update_math();
    });

    function bind_request(btn, url, handler, condition) {
        $('#btn-' + btn).click(function() {
            var input = input_textarea.val();

            if (pending_request || !$.trim(input).length
                    || (condition && !condition())) {
                return;
            }

            show_loader();
            clear_error();

            // TODO: disable input box and enable it when this ajax request is done
            // (on failure and success).
            $.post(url, {data: input}, function(response) {
                if (!response)
                    return;

                if ('error' in response)
                    return report_error(response);

                handler(response);
                hide_loader();
                clear_error();
            }, 'json').error(report_error);
        });
    }

    // No need to show a hint if there is already one at the end of the
    // calculation
    function no_hint_displayed() {
        return !pretty_print.children(':last').hasClass('hint');
    }

    bind_request('hint', '/hint', function(response) {
        append_hint(response.hint);
        input_textarea.focus();
    }, no_hint_displayed);

    bind_request('step', '/step', function(response) {
        if ('step' in response) {
            append_input(response.step);
            trigger_update = true;
        }

        if('hint' in response && no_hint_displayed())
            append_hint(response.hint);

        input_textarea.focus();
    });

    bind_request('validate', '/validate', function(response) {
        var math_lines = pretty_print.find('div.box');
        var i = 0;

        // Remove the status indicator from all remaining lines.
        for(; i < math_lines.length; i++)
            set_status(math_lines[i]);

        i = 0;

        // Check if the first line has a correct syntax, since there is
        // nothing to validate here.
        if (i < math_lines.length && i <= response.validated) {
            set_status(math_lines[i], STATUS_SUCCESS);
            i++;
        }

        // Mark every line as {wrong,no-progress,correct,error}.
        for (; i < math_lines.length && i <= response.validated; i++)
            set_status(math_lines[i], response.status[i - 1]);

        if (i < math_lines.length) {
            // Mark the current line as wrong.
            set_status(math_lines[i], STATUS_FAILURE);
        }
    });

    bind_request('answer', '/answer', function(response) {
        if ('steps' in response) {
            for(i = 0; i < response.steps.length; i++) {
                cur = response.steps[i];

                if ('step' in cur)
                    append_input(cur.step);

                if('hint' in cur)
                    append_hint(cur.hint);

                trigger_update = true;
                window.update_math();
            }
        }

        if('hint' in response)
            append_hint(response.hint);

        input_textarea.focus();
    });
})(jQuery);
