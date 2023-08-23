document$.subscribe(function() {
    // get the original serves value
    const parse_serves = RegExp('Serves: +([0-9]+)(.*)')
    orig = parse_serves.exec($('#serves').text())
    console.log(orig)
    $('#serves').attr('data-original', orig[1])
    $('#serves').text(orig[0].replace(orig[1], '  ').replace(orig[2], ''))
    // create the +/- buttons
    // these two svgs are based on the material-plus and material-minus icons
    const plus = '<span class="twemoji"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2Z"></path></svg></span>'
    const minus = '<span class="twemoji"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M19 13H5v-2h14v2Z"></path></svg></span>'
    const increment = function(){
        $('#serves-input').val(parseInt($('#serves-input').val())+1)
        $('#serves-input').trigger("change")
    }
    const decrement = function(){
        $('#serves-input').val(parseInt($('#serves-input').val())-1)
        $('#serves-input').trigger("change")
    }
    const plus_button = '<a id="plus-button" class="md-button md-button--primary" style="padding: .5em .7em;">' + plus + '</a>'
    const minus_button = '<a id="minus-button" class="md-button md-button--primary" style="padding: .5em .7em;">' + minus + '</a>'
    const input = '<input class="md-typeset form-control" type="text" min="0" id="serves-input">'
    $('#serves').append(minus_button)
    $('#minus-button').click(decrement)
    $('#serves').append(input)
    $('#serves-input').val(parseInt(orig[1]))
    $('#serves').append(plus_button)
    $('#serves').append(orig[2])
    $('#plus-button').click(increment)
    // these elements (with ingredient-num class already attached) are those
    // found in line, and we just need to wrap them in <a> tag and encode their original values
    $('.ingredient-num').each(function(idx, elem){
        $(elem).wrap('<a/>')
        $(elem).attr('data-original', $(elem).text())
    })
    // encode original ingredient values and wrap them in <a> tag
    const ingredients = $('#ingredients').next().children()
    const parse_ingr = RegExp('([0-9-. ]+) ')
    $.each(ingredients, function(idx, elem){
        orig = parse_ingr.exec($(elem).text())
        if (orig !== null) {
            $(elem).text($(elem).text().replace(parse_ingr, function(match) {
                return " "
            }))
            $(elem).prepend(`<a class='ingredient-num' data-original=${orig[1]}>${orig[1]}</a>`)
        }
    })
    // when the serves number changes, update the
    $('#serves-input').on("change", function(){
        orig = $('#serves').attr('data-original')
        new_val = $('#serves-input').val()
        ratio = parseFloat(new_val) / parseFloat(orig);
        $(".ingredient-num").each(function(idx, elem){
            orig = $(elem).attr('data-original').split('-')
            new_val = $(elem).text().split('-').map((x, i) => parseFloat(orig[i])*ratio).join('-')
            $(elem).text(new_val)
        })
    })
})
