var quantity_input = $('input')
var price_text = $('.price')
var prices = []
var subtotal = 0
var shipping = 60
var quantity = []

function convert_text_to_int(price_text){
    // console.log("Called")
    var x =0
    for(var i=0;i<price_text.length;i++)
    {
        // console.log(price_text[i])
        if(price_text[i]>='0'&&price_text[i]<='9')
        {
            var p = price_text[i]-'0'
            x= x*10 + p
        }
    }
    // console.log(x)
    return x
}
$(document).ready(function () {
    console.log(quantity_input)
    console.log(price_text)
    for (var i = 2; i < quantity_input.length-1; i++) {
        // console.log("Here")
        prices[i - 2] = convert_text_to_int(price_text.eq(i - 2).text()) / parseInt(quantity_input.eq(i).val())
        quantity[i - 2] = parseInt(quantity_input.eq(i).val())
        subtotal += prices[i - 2] * quantity[i - 2]
    }
    console.log(quantity)
    console.log(prices)
    if (subtotal === 0) {
        shipping = 0
    } else {
        shipping = 60
    }
    price_text.eq(-4).text(subtotal + " Tk")
    price_text.eq(-2).text(shipping + " Tk")
    price_text.eq(-1).text((subtotal + shipping) + " Tk")
})

quantity_input.bind("input", function () {
    var id = $(this).index()
    console.log(id)
    if (id === 0) {
        return
    }

    if (parseInt($(this).val()) <= 0) {
        $(this).val(1)
    }
    subtotal = 0
    for (var i = 2; i < quantity_input.length-1; i++) {
        quantity[i - 2] = parseInt(quantity_input.eq(i).val())
        price_text.eq(i - 2).text((prices[i - 2] * quantity[i - 2]) + " Tk")
        subtotal += prices[i - 2] * quantity[i - 2]
    }
    if (subtotal === 0) {
        shipping = 0
    } else {
        shipping = 60
    }
    price_text.eq(-4).text(subtotal + " Tk")
    price_text.eq(-2).text(shipping + " Tk")
    price_text.eq(-1).text((subtotal + shipping) + " Tk")
    quantity_input.eq(quantity_input.length-1).val((subtotal + shipping))
})