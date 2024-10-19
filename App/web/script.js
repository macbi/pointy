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
            $('#btn_map').removeClass('btn-outline-secondary').addClass('btn-secondary');
            $('#btn_kml').removeClass('btn-outline-success').addClass('btn-success');
            $('#btn_export').removeClass('btn-outline-success').addClass('btn-success');
            $('#btn_map').click();
            eel.log({ "type": "info", "message": 'If map shows wierd points position, try changing CRS.' })
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
        $("#btn_height").prop('disabled', true).empty().append('<span class="spinner-border spinner-border-sm"></span><span role="status"> Fetching...</span>');
        let input_crs = $("#coordinate-select").val();
        eel.addHeightToDataFrame(input_crs)().then((result) => {
            $('#display').empty().append(result);
            $("#btn_height").prop('disabled', false).empty().append('<span role="status">Get Height</span>');
            $('#btn_map').click();
        }).catch((result) => {
            console.log("This is the repr(e) for an exception " + result.errorText);
            console.log("This is the full traceback:\n" + result.errorTraceback);
        });
    });

    $("#btn_map").click(function () {
        let input_crs = $("#coordinate-select").val();
        eel.showPointsOnMap(input_crs)().then((result) => { }).catch((result) => {
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

            $('#file').val(file);

            eel.log({ "type": "", "message": 'File selected. Please choose sheet and columns.' })

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
            switch (items[i].type) {
                case 'success':
                    color = 'success';
                    itemPrefix = '<li class="list-group-item list-group-item-success">';
                    icon = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-check-circle" viewBox="0 0 16 16">
  <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14m0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16"/>
  <path d="m10.97 4.97-.02.022-3.473 4.425-2.093-2.094a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-1.071-1.05"/>
</svg>`;
                    break;
                case 'error':
                    color = 'danger';
                    itemPrefix = '<li class="list-group-item list-group-item-danger">';
                    icon = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-exclamation-diamond" viewBox="0 0 16 16">
  <path d="M6.95.435c.58-.58 1.52-.58 2.1 0l6.515 6.516c.58.58.58 1.519 0 2.098L9.05 15.565c-.58.58-1.519.58-2.098 0L.435 9.05a1.48 1.48 0 0 1 0-2.098zm1.4.7a.495.495 0 0 0-.7 0L1.134 7.65a.495.495 0 0 0 0 .7l6.516 6.516a.495.495 0 0 0 .7 0l6.516-6.516a.495.495 0 0 0 0-.7L8.35 1.134z"/>
  <path d="M7.002 11a1 1 0 1 1 2 0 1 1 0 0 1-2 0M7.1 4.995a.905.905 0 1 1 1.8 0l-.35 3.507a.552.552 0 0 1-1.1 0z"/>
</svg>`;
                    break;
                case 'warning':
                    color = 'warning';
                    itemPrefix = '<li class="list-group-item list-group-item-warning">';
                    icon = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-shield-exclamation" viewBox="0 0 16 16">
  <path d="M5.338 1.59a61 61 0 0 0-2.837.856.48.48 0 0 0-.328.39c-.554 4.157.726 7.19 2.253 9.188a10.7 10.7 0 0 0 2.287 2.233c.346.244.652.42.893.533q.18.085.293.118a1 1 0 0 0 .101.025 1 1 0 0 0 .1-.025q.114-.034.294-.118c.24-.113.547-.29.893-.533a10.7 10.7 0 0 0 2.287-2.233c1.527-1.997 2.807-5.031 2.253-9.188a.48.48 0 0 0-.328-.39c-.651-.213-1.75-.56-2.837-.855C9.552 1.29 8.531 1.067 8 1.067c-.53 0-1.552.223-2.662.524zM5.072.56C6.157.265 7.31 0 8 0s1.843.265 2.928.56c1.11.3 2.229.655 2.887.87a1.54 1.54 0 0 1 1.044 1.262c.596 4.477-.787 7.795-2.465 9.99a11.8 11.8 0 0 1-2.517 2.453 7 7 0 0 1-1.048.625c-.28.132-.581.24-.829.24s-.548-.108-.829-.24a7 7 0 0 1-1.048-.625 11.8 11.8 0 0 1-2.517-2.453C1.928 10.487.545 7.169 1.141 2.692A1.54 1.54 0 0 1 2.185 1.43 63 63 0 0 1 5.072.56"/>
  <path d="M7.001 11a1 1 0 1 1 2 0 1 1 0 0 1-2 0M7.1 4.995a.905.905 0 1 1 1.8 0l-.35 3.507a.553.553 0 0 1-1.1 0z"/>
</svg>`;
                    break;
                case 'info':
                    color = 'info';
                    itemPrefix = '<li class="list-group-item list-group-item-info">';
                    icon = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-info-square" viewBox="0 0 16 16">
  <path d="M14 1a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1zM2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2z"/>
  <path d="m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0"/>
</svg>`;
                    break;
                default:
                    color = 'light';
                    icon = `<img src="pointy_logo.svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">`;
            }

            let button = '';
            if (items[i].actionId) {
                console.log(items[i].actionId);
                button = `<button type="button" class="btn btn-${color} btn-sm" id="${items[i].actionId}">Rerun</button>`;
            }

            $item = $(`<li class="list-group-item list-group-item-${color}"><div class="hstack gap-3">`+ icon +`<div class="me-auto">` + items[i].message + '</div>' + button + '</div></li>');
            $list.append($item);
        }

        return $list;
    }

    function updateList(id, items) {
        $('#' + id).empty().append(buildList(items));
    }

    $("#coordinate-select").change(function () {
        crsName = $("#coordinate-select option:selected").text();
        $('#btn_map').click();
        eel.log({ "type": "warning", "message": `You selected ${crsName} CRS. It will be used for all operations now.` });
    });

    $(document).on('click', '#btn_addMissingHeights', function () {
        console.log("Clicked");
        let input_crs = $("#coordinate-select").val();
        eel.addMissingHeights(input_crs)().then((result) => {
            console.log(result);
            $('#display').empty().append(result);
            $('#btn_map').click();
        }).catch((result) => {
            console.log("This is the repr(e) for an exception " + result.errorText);
            console.log("This is the full traceback:\n" + result.errorTraceback);
        });
    });

    $("#pointy_logo").click(function () {
        $("#helpModal").modal('show');
    });


    $("#helpModal").modal({ show: false});

    $(document).on('click', '#btn_modal_repeat', function () {
        let img = $('#img_cat');
        let newSrc = 'https://cataas.com/cat?width=300&height=300&timestamp=' + new Date().getTime();
        img.attr('src', newSrc);
    });

    eel.expose(updateProgress);
    eel.expose(updateList);

    eel.log({ "type": "", "message": 'App started. Please load Excel file.'})

}); 