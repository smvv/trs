(function ($) {
    var QUEUE = MathJax.Hub.queue;  // shorthand for the queue
    var math = null; // the element jax for the math output

    // Hide and show the box (so it doesn't flicker as much)
    var hide_box = function () {box.style.visibility = "hidden"}
    var show_box = function () {box.style.visibility = "visible"}
    var trigger_update = true;

    // Initialise codemirror environment
    var input_textarea = document.getElementById("MathInput"),
        input_box = CodeMirror.fromTextArea(input_textarea, {
            value: '',
            mode:  'r',
            matchBrackets: true,
            onChange: function(f) { trigger_update = true; }
        });

    // Get the element jax when MathJax has produced it.
    QUEUE.Push(function () {
        math = MathJax.Hub.getAllJax("MathOutput")[0];
        box = document.getElementById("box");
        show_box();

        // The onchange event handler that typesets the math entered
        // by the user.  Hide the box, then typeset, then show it again
        // so we don't see a flash as the math is cleared and replaced.
        var update_math = function (tex) {
            //var start = '\\begin{equation}\\begin{split}';
            //var end = '\\end{split}\\end{equation}';
            //tex = start + tex.replace(/\n/g, end + start) + end;
            //tex = '\\displaystyle{' + tex.replace(/\n/g, '\\\\') + '}';
            //tex = '`' + tex.replace(/\n/g, '\\\\') + '`';
            QUEUE.Push(hide_box, ["Text", math, tex], show_box);
        }

        setInterval(function() {
            if (trigger_update) {
                trigger_update = false;
                update_math(input_box.getValue());
            }
        }, 50);
    });
})(jQuery);
