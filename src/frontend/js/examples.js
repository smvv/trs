(function($) {
    function Example(actions) {
        this.actions = actions;
        this.actions.push(this.destroy_popover);
    }

    var current_example;

    $.extend(Example.prototype, {
        destroy_popover: function() {
            this.current_elem && this.current_elem.popover('destroy');
        },
        show_popover: function(selector, alignment, description) {
            this.destroy_popover();
            this.current_elem = $(selector);
            this.current_elem.popover({
                trigger: 'manual',
                placement: alignment,
                html: true,
                title: '<button id="next-example-step" class="btn btn-primary">next</button><div class="clear"/>',
                content: description,
                animation: false
            }).popover('show');
        },
        play: function() {
            this.current_action = 0;
            current_example = this;
            this.next();
        },
        next: function() {
            if (this.current_action < this.actions.length)
                $.proxy(this.actions[this.current_action++], this)();
        }
    });

    $('#next-example-step').live('click', function() {
        current_example.next();
    });

    function clear_input() {
        $('#math-input').val('').change();
        window.update_math && window.update_math();
        $('#math-input').focus();
        this.next();
    }

    function append_line(line) {
        return function() {
            $('#math-input')
                .val($.trim($('#math-input').val() + '\n' + line))
                .change();
            window.update_math();
            this.next();
        };
    }

    function erase_line() {
        var value = $.trim($('#math-input').val());

        for (var i = value.length - 1; i >= 0; i--) {
            if (value.charAt(i) == '\n') {
                value = value.substring(0, i);
                break;
            }
        }

        $('#math-input').val(value).change();
        window.update_math();
        this.next();
    }

    function label_elem(selector, alignment, description) {
        return function() {
            this.show_popover(selector, alignment, description);
        };
    }

    function label_button(btn, description) {
        return label_elem('#btn-' + btn, 'bottom', description);
    }

    function label_input(description) {
        return label_elem('#math-input', 'left', description);
    }

    function label_pretty_print(description) {
        return label_elem('#pretty-print', 'right', description);
    }

    function click_button(btn) {
        return function() {
            console.log($('#btn-' + btn));
            this.destroy_popover();
            $('#btn-' + btn).click();
            this.next();
        };
    }

    var tutorial = [
        clear_input,
        label_input('You type expressions in this area.'),
        label_pretty_print('Expressions you type in the input area appear '
                           + 'here in pretty-printed mathematical notation. '
                           + 'Click &ldquo;next&rdquo; to try it out!'),
        append_line('x^2 + 4x - 7'),
        label_pretty_print('Neat huh...'),
        label_elem('#btn-answer', 'right', 'These controls allow you to '
                                           + 'communicate to the system.'),
        label_button('validate', 'Validate that the steps you have done so far '
                                 + 'are correct.'),
        label_button('hint', 'Ask the system for a hint on how to continue when '
                             + 'you are stuck.'),
        label_button('step', 'Let the system sort out the next step in your '
                             + 'calculation'),
        label_button('answer', 'Let the system do your entire calculation.'),
        label_elem('#examples', 'bottom', 'Here are some examples that show you '
                                          + 'how to use the interface properly.'),
    ];

    $('#tutorial').click(function() {
        new Example(tutorial).play();
    });

    var examples = [[
        clear_input,
        label_input('This example shows how you can interactively rewrite an '
                    + 'expression with a little help by the system. Start '
                    + 'by entering an expression.'),
        append_line('[sin(x) + sin(x)]\''),
        label_input('Rewrite the expression as far as you can.'),
        append_line('[2sin(x)]\''),
        label_button('validate', 'Validate that your calculation is correct.'),
        click_button('validate'),
        label_pretty_print('All icons should be green.'),
        label_button('hint', 'When you\'re stuck, ask for a hint.'),
        click_button('hint'),
        label_pretty_print('The hint appears here, try to apply it.'),
        //label_button('step', 'If you do not understand the hint, let the '
        //                     + 'system apply it for you.'),
        //click_button('step'),
        //label_pretty_print('Understand it now? You may want to erase the last '
        //                   + 'line and try for yourself!'),
        //erase_line,
        //label_input('Take a step back, try to apply the hint yourself.'),
        append_line('3[sin(x)]\''),
        label_button('validate', 'Again, validate that your calculation is '
                                 + 'correct.'),
        click_button('validate'),
        label_pretty_print('Oops! You made an error, you should fix it before '
                           + 'continuing.'),
        erase_line,
        append_line('2[sin(x)]\''),
        click_button('validate'),
        label_input('Continue rewriting the expression.'),
        append_line('(1 + 1)[sin(x)]\''),
        label_input('This step is correct, but makes no sense because it does '
                    + 'not help you any further.'),
        label_button('validate', 'The validator will detect this too.'),
        click_button('validate'),
        label_pretty_print('The orange icon indicates that you have not made '
                           + 'any progress.'),
        label_input('Go back and try something else.'),
        erase_line,
        append_line('2cos(x)'),
        label_button('validate', 'Keep validating...'),
        click_button('validate'),
        label_pretty_print('Yay! This seems to be the answer you were looking '
                           + 'for.'),
        label_button('hint', 'Assert that you are done by checking if there '
                     + 'are any hints left.'),
        click_button('hint'),
    ], [
        clear_input,
        label_input('This example shows how you can let the system rewrite an '
                    + 'expression step-wise. Start with an expression.'),
        append_line('[sin(x) + sin(x)]\''),
        label_button('step', 'Ask the system to execute a step.'),
        click_button('step'),
        label_pretty_print('The step will be displayed with a preceding hint.'),
        label_button('step', 'You can keep asking for steps until the '
                             + 'calculation is done.'),
        click_button('step'),
        label_button('step', 'You can keep asking for steps until the '
                             + 'calculation is done.'),
        click_button('step'),
        label_button('step', 'You can keep asking for steps until the '
                             + 'calculation is done.'),
        click_button('step'),
    ], [
        clear_input,
        label_input('This example shows how you can let the system rewrite an '
                    + 'expression fast. Start with an expression.'),
        append_line('[sin(x) + sin(x)]\''),
        label_button('answer', 'Ask the system for an answer.'),
        click_button('answer'),
        label_pretty_print('All steps will be displayed with preceding hints.'),
    ]];

    $('#examples .dropdown-menu a').each(function(i) {
        $(this).click(function() {
            new Example(examples[i]).play();
        });
    });

    if (location.search.substr(0, 3) == '?t=') {
        var t = parseInt(decodeURIComponent(location.search.substr(3)));

        if (t == 0)
            new Example(tutorial).play();
        else if (t > 0 && t <= examples.length)
            new Example(examples[t - 1]).play();
    }
})(jQuery);
