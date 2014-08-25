$('.dynamic-carousel').each(function () {
    var $this = $(this);
    $this.css({
        "width": ($this.height() * 0.75) + "px"
    })
});
