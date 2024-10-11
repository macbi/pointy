$(function () {

    eel.expose(say_hello_js);               // Expose this function to Python
    function say_hello_js(x) {
        console.log("Hello from " + x);
    }
    say_hello_js("Javascript World!");
    eel.handleinput("connected!");  // Call a Python function

    $("#btn_start").click(function () {
        getPathToData();
    });

    $("#btn_data").click(function () {
        let x = $("#x_slct").val();
        let y = $("#y_slct").val();
        let name = $("#name_slct").val();
        let sheet = $("#sheet_slct").val();
        let file = $("#file").val();
        console.log(x, y, name, sheet, file);
        eel.getHTMLTable(file, sheet, [name, x, y])().then((result) => {
            $('#progress').empty();
            $('#display').empty().append(result);
            $('#btn_data').removeClass('btn-secondary').addClass('btn-outline-secondary');
            $('#btn_height').prop('disabled', false);
            $('#btn_kml').prop('disabled', false);
            $('#btn_map').prop('disabled', false);
            $('#btn_export').prop('disabled', false);
            $('#btn_height').removeClass('btn-outline-secondary').addClass('btn-secondary');
            $('#btn_kml').removeClass('btn-outline-secondary').addClass('btn-secondary');
            $('#btn_map').removeClass('btn-outline-secondary').addClass('btn-secondary');
            $('#btn_export').removeClass('btn-outline-secondary').addClass('btn-secondary');
            $('#btn_map').click();
            eel.log({ "type":"info","message":'If map shows wierd points position, try changing CRS.'})
        }).catch((result) => {
            console.log("This is the repr(e) for an exception " + result.errorText);
            console.log("This is the full traceback:\n" + result.errorTraceback);
        }
        );

    });

    $("#btn_export").click(function () {
        eel.saveDataFrameToExcel()().then((result) => {

        }).catch((result) => {
            console.log("This is the repr(e) for an exception " + result.errorText);
            console.log("This is the full traceback:\n" + result.errorTraceback);
        });
    });

    $("#btn_height").click(function () {
        $("#btn_height").prop('disabled', true).empty().append('<span class="spinner-border spinner-border-sm"></span><span role="status">Fetching...</span>');
        let input_crs = $("#coordinate-select").val();
        eel.addHeightToDataFrame(input_crs)().then((result) => {
            $('#display').empty().append(result);
            $("#btn_height").prop('disabled', false).empty().append('<span role="status">Get Height</span>');
        }).catch((result) => {
            console.log("This is the repr(e) for an exception " + result.errorText);
            console.log("This is the full traceback:\n" + result.errorTraceback);
        });
    });

    $("#btn_map").click(function () {
        let input_crs = $("#coordinate-select").val();
        eel.showPointsOnMap(input_crs)().then((result) => {  }).catch((result) => {
            console.log("This is the repr(e) for an exception " + result.errorText);
            console.log("This is the full traceback:\n" + result.errorTraceback);
        });
    });

    $("#btn_kml").click(function () {
        let input_crs = $("#coordinate-select").val();
        eel.saveDataFrameToKML(input_crs)().then((result) => { }).catch((result) => {
            console.log("This is the repr(e) for an exception " + result.errorText);
            console.log("This is the full traceback:\n" + result.errorTraceback);
        });
    });

    function updateProgress(progress) {
        $('#progress').text(progress);
    }

    function getPathToData() {
    eel.getFilePath()((file) => {
        if (file === "") {
            return;
        }
        
        $('#file').val( $('#file').val() + file );

        eel.log({ "type":"","message":'File selected. Please choose sheet and columns.'})

        eel.getExcelSheetNames(file)((result) => {
            console.log(result);
            $('#sheet').empty().append(buildSelect("sheet_slct", result).on('change', function () {
                // refresh name, x, y selects
                let selectedSheet = $(this).val();
                console.log(selectedSheet); 
                console.log(file);

                eel.getExcelSheetHeaders(file, selectedSheet)((result) => {
                    console.log(result);
                    $('#name').empty().append(buildSelect("name_slct", result, 0));
                    $('#inpX').empty().append(buildSelect("x_slct", result, 1));
                    $('#inpY').empty().append(buildSelect("y_slct", result, 2));
                })
            }));

            let selectedSheet = $('#sheet_slct')[0].value;

            eel.getExcelSheetHeaders(file, selectedSheet)((result) => {
                console.log(result);
                $('#name').empty().append(buildSelect("name_slct", result, 0));
                $('#inpX').empty().append(buildSelect("x_slct", result, 1));
                $('#inpY').empty().append(buildSelect("y_slct", result, 2));
            })
        });
        $('#btn_data').prop('disabled', false);
        $('#btn_data').removeClass('btn-outline-secondary').addClass('btn-secondary');
        $('#btn_start').removeClass('btn-success').addClass('btn-outline-success');
    });
}

function buildSelect(id, options, selectedValue = 0) {

    var $select = $('<select id="' + id + '"></select>');
    var $option;

    for (let i = 0; i < options.length; i++) {
        $option = $('<option value="' + options[i] + '">' + options[i] + '</option>');
        if (i === selectedValue) {
            $option.attr('selected', true);
        }
        $select.append($option);
    }

    return $select;
}

function buildList(items) {
    var $list = $('<ul class="list-group""></ul>');
    var $item;

    for (let i = 0; i < items.length; i++) {
        switch(items[i].type) {
            case 'success':
                itemPrefix = '<li class="list-group-item list-group-item-success">';
                break;
            case 'error':
                itemPrefix = '<li class="list-group-item list-group-item-danger">';
                break;
            case 'warning':
                itemPrefix = '<li class="list-group-item list-group-item-warning">';
                break;
            case 'info':
                itemPrefix = '<li class="list-group-item list-group-item-info">';
                break;
            default:
                itemPrefix = '<li class="list-group-item list-group-item-light">';
        }

        $item = $(itemPrefix + items[i].message + '</li>');
        $list.append($item);
    }

    return $list;
}

function updateList(id, items) {
    $('#' + id).empty().append(buildList(items));
}

$("#coordinate-select").change(function () {
    crsName = $("#coordinate-select option:selected").text();
   eel.log({"type":"warning","message": `You selected ${crsName} CRS. It will be used for all operations now.`});
});


eel.expose(updateProgress);
eel.expose(updateList);

eel.log({ "type":"","message":'App started. Please load Excel file.'})

}); 