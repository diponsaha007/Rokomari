var price_text = $('.price')
var subtotal = 0

$(document).ready(function () {
    for (var i = 0; i < price_text.length - 2; i++) {
        subtotal += parseInt(price_text.eq(i).text().substring(0))
    }
    price_text.eq(-2).text(price_text.length - 2)
    price_text.eq(-1).text((subtotal) + " Tk")
})