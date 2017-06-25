	jsPlumb.ready(function() {


    /////////////////////////  GLOBAL  //////////////////////////////

    jsPlumb.registerConnectionType("selected", {
      paintStyle:{ strokeStyle:"lawngreen", lineWidth:2 },
      hoverPaintStyle:{ strokeStyle:"lawngreen", lineWidth:3 },
      ConnectionOverlays: [ [ "Label", { label: "FOO", id: "label", cssClass: "aLabel" }]],
			overlays:[
                    ["Arrow" , { width:8, length:8, foldback: 1, location:1 }]
                ]
    });

    jsPlumb.registerConnectionType("generic", {
      paintStyle:{ strokeStyle:"dimgray", lineWidth:2  },
      hoverPaintStyle:{ strokeStyle:"dimgray", lineWidth:3 },
      ConnectionOverlays: [ [ "Label", { label: "FOO", id: "label",location:[0.5, 0.5], cssClass: "aLabel" }]],
			overlays:[
                    ["Arrow" , { width:8, length:8, foldback: 1, location:1 }]
                ]
    });

	  jsPlumb.setContainer($('#container'));



	  var boxCount = 0;
    var connectionSelected;
    var listening = true;
		var editing = false;
    allStates = new Array();
    var Graphique = {};

		var libLoaded = false;
		var mediasLoaded = false;


		var urlbase = '';
		//var urlbase = 'http://192.168.0.19:8080';

    $("#signalEdit").hide();
    $('#newBox').hide();
    $('#editBox').hide();
		$('#editText').hide();

    //////////////////////// CODE MIRROR ////////////////////////////////
      var codeAdd = CodeMirror.fromTextArea(document.getElementById("code"), {
        mode: {name: "python",
               version: 3,
               singleLineStringErrors: false},
        lineNumbers: true,
        lineWrapping: true,
        indentUnit: 4,
        matchBrackets: true
    });

      var codeEdit = CodeMirror.fromTextArea(document.getElementById("codeed"), {
        mode: {name: "python",
               version: 3,
               singleLineStringErrors: false},
        lineNumbers: true,
        lineWrapping: true,
        indentUnit: 4,
        matchBrackets: true
    });


    ////////////////////////// LIBRARY //////////////////////////////////
    /////////////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////


		////////////////////////// CATEGORY //////////////////////////////////
    var cat1 = {name:'AUDIO', color:'4169E1'};
    var cat2 = {name:'VIDEO', color:'008080'};
    var cat3 = {name:'LUMIERE', color:'F0E080'};
    var cat4 = {name:'REMOTE', color:'FFA07A'};
    var cat5 = {name:'TITREUR', color:'CD5C5C'};
    var cat6 = {name:'CARTE', color:'3F5F5F'};//2F4F4F
    var cat7 = {name:'GENERAL', color:'696969'};
		var cat8 = {name:'DEVICE', color:'708090'};
		var cat9 = {name:'SCENE', color:'66CDAA'};
    var allCats = new Array();
    allCats.push(cat1);
    allCats.push(cat2);
    allCats.push(cat3);
    allCats.push(cat4);
    allCats.push(cat5);
    allCats.push(cat6);
    allCats.push(cat7);
		allCats.push(cat8);
		allCats.push(cat9);
	  $.each(allCats, function(index,cat){
	    $('#addCat,#editCat,#selCat').append(('<option value="'+index+'">'+cat.name+'</option>'));
	  });

    var allBoxes = new Array();
    loadLibrary();
		////////////////////////// BUILD //////////////////////////////////

    function buildLibrary(){
      console.log("BUILDING");

      $('#lib').empty();
      $.each(allBoxes, function(box){
        var box = '<div id="'+this.name+'"class="lib '+this.category+'" category="'+this.category+'">'+this.name+'</div>'
        $('#lib').append(box);

        var theColor;
        for (var i = 0, len = allCats.length; i < len; i++) {
          if (allCats[i].name === this.category) { theColor = allCats[i].color; }
        }
        $('.'+this.category).css('background-color', '#'+theColor);
        sortLibrary();

      });
      draggable();
      editable();
    }

    ////////////////////////// VIEW //////////////////////////////////

    $('#selCat').change(function(){
      sortLibrary();
    });
    function sortLibrary(){
      var selectedCategory = $('#selCat option:selected').text();
      $('.lib').hide();
      $('.'+selectedCategory).show();
      $('#addCat').val( $('#addCat option').filter(function(){ return $(this).html() == selectedCategory; }).val() );
      $("#editBox").hide();
    }

    $("#container").click(function(e){
      $("#newBox").hide();
      $("#editBox").hide();
      $("#informations").hide();
    });
    ///////////////////////////   INFOS  /////////////////////////////
    $("#informations").hide();
    $('#closeInfos').on('click',function(){
      $('#informations').fadeOut(200);
    });
    $('#openInfos').on('click',function(){
      $('#informations').fadeIn(200);
    });

    ///////////////////////////   NEW  ///////////////////////////////

    $('#openAdder').on('click',function(){
			unselectAll();
      $('#informations').hide();
			$('#editText').hide();
      $('#editBox').hide();
      $('#newBox').fadeIn(200);
      $('#addName').val("NAME");
      $('#addArg1').val("arg1");
      $('#addArg2').val("arg2");
      $('#addArg3').val("arg3");
      codeAdd.setValue('\n\n\n\n\n\n\n\n\n');
      codeAdd.setValue('#Write Python Here...');
    });
    $('#cancelAdd').on('click',function(){
      $('#newBox').fadeOut(200);
    });

    $('#addBox').on('click',function(){
      $('#newBox').fadeOut(200);
      var nem = $('#addName').val();
      var cat = $('#addCat option:selected').text();
      var disp = $('#addDisposList').prop('checked');
      var med = $('#addMediasList').prop('checked');
      var arg1 = $('#addArg1').val(); var arg2 = $('#addArg2').val(); var arg3 = $('#addArg3').val();
      var args = [arg1, arg2, arg3];
      var cd = codeAdd.getValue();
      var newBox = {name:nem, category:cat, dispos: disp, medias: med, arguments:args, code:cd};
      allBoxes.push(newBox);
      buildLibrary();
      saveLibrary();
    });

    $("input[type='text']").on("click", function () {
       $(this).select();
    });

    //////////////////////////   EDIT  ///////////////////////////////
    var boxEdited;
    var indexEdited;
    function editable(){
      $( ".btn2").unbind( "click" );
      $('.lib').on('click', function(){
				unselectAll();
        $('#newBox').hide();
				$('#editText').hide();
        $('#informations').hide();
        $('#editBox').fadeIn(200);
        var nameEdited = $(this).attr('id');
        $("#editName").val(nameEdited);
        for (var i = 0, len = allBoxes.length; i < len; i++) {
            if (allBoxes[i].name === nameEdited) { boxEdited = allBoxes[i]; indexEdited = i;}
        }
        $('#editCat').val(
          $('#editCat option').filter(function(){ return $(this).html() == boxEdited.category; }).val()
        );
        $('#editDisposList').prop('checked', boxEdited.dispos);
        $('#editMediasList').prop('checked', boxEdited.medias);
        $('#editArg1').val(boxEdited.arguments[0]);
        $('#editArg2').val(boxEdited.arguments[1]);
        $('#editArg3').val(boxEdited.arguments[2]);
        codeEdit.setValue('\n\n\n\n\n\n\n\n\n');
        codeEdit.setValue(boxEdited.code);
        });
    }

    editable();

    $('#modifBox').on('click', function(){
      allBoxes[indexEdited].name = $('#editName').val();
      allBoxes[indexEdited].category = $('#editCat option:selected').text();
      allBoxes[indexEdited].dispos =$('#editDisposList').prop('checked');
      allBoxes[indexEdited].medias =$('#editMediasList').prop('checked');
      allBoxes[indexEdited].arguments = [ $('#editArg1').val(), $('#editArg2').val(), $('#editArg3').val(), ];
      allBoxes[indexEdited].code = codeEdit.getValue();
      buildLibrary();
      $('#editBox').fadeOut(200);
      saveLibrary();
    });

    $('#cancelEdit').on('click',function(){
      $('#editBox').fadeOut(200);
    });

    var indexToRemove;
    $('#deleteBox').on('click', function(){
      allBoxes.splice(indexEdited,1);
      buildLibrary();
      saveLibrary();
      $('#editBox').fadeOut(200);
      });


    /////////////////////////// SAVE LIB ///////////////////////////////

    function saveLibrary(){
			// On sauve en local uniquement les fonctions persos,
			// --> Si mgr en modifie une, son nom se répercute
		  var userBoxes = [];
      $.each(allBoxes,function(index,box){
				if (!box.hard) userBoxes.push(box);
			});

			$.ajax({
          url: "data/save.php",
          dataType: "json",
          type: "POST",
          data: {
						contents: JSON.stringify(userBoxes),
	          filename: 'library',
						timestamp: $.now(),
						type: 'library'
					}
      })
      .done(function(reponse)
      {
          if (reponse.status == 'success')
          {
						//$('#serverDisplay').html( 'Saved : <br> '+ JSON.stringify(allBoxes) );
					}
      });
    }
    /////////////////////////// LOAD LIB ///////////////////////////////
		var lib = new Array();
    function loadLibrary() {
      //allBoxes=[];
        $.ajax({
            url: "data/load.php",
            dataType: "json",
            type: "POST",
            data: {
                filename: 'library',
								type: 'library'
            }
        })
        .done(function(reponse) {
            if (reponse.status == 'success')
            {
                lib = JSON.parse(reponse.contents);
					      $.each(lib, function( index, box ) {
					        var tempbox = {name:box.name, category:box.category, dispos: box.dispos, medias: box.medias, arguments: box.arguments, code:box.code};
					        allBoxes.push(tempbox);
					      });
								buildLibrary();

            }
        });
    }


  	//////////////////////// SIGNALS //////////////////////////////
		allSignals = ['SGN1','SGN2','SGN3','SGN4'];
		function updateSignals(){
			$('#signalselector').empty();
			$.each(allSignals, function(index,signal){
				$('#signalselector').append(('<option value="'+index+'">'+signal+'</option>'));
			});
		}
		updateSignals();


    //////////////////////// MERGE WITH MGR //////////////////////////////
		var hardlib = new Array();
		function loadExtLib(){
			$.ajax({
				type: 'GET',
				timeout: 1000,
				url: urlbase+"/library",
				dataType: "jsonp"
			}).done(function(data) {
				hardlib = data.functions;
				mergeLibrary();
				allSignals = data.signals;
				console.log("loading signals");
				updateSignals();
				loadScenario();
			}).fail(function(){
				loadScenario();
			});
		}
		loadExtLib();

		function mergeLibrary(){
			//COMPARE LIB
      var indexedBoxes = {};
			$.each(allBoxes, function( index, box ) {
        indexedBoxes[box.name+box.category] = box;
      });
			$.each(hardlib, function( index, box ) {
        var tempbox = box;
        indexedBoxes[tempbox.name+tempbox.category] = tempbox;
      });
			allBoxes = [];
			$.each(indexedBoxes, function( index, box ) {
        allBoxes.push(box);
      });
			//COMPARE CATEGORIES
	    var indexedLib = {};
			$.each(hardlib, function( index, box ) {
	      var tempLib = {name: box.category, color:'444444'};
	      indexedLib[tempLib.name] = tempLib;
	    });
			$.each(allCats, function( index, cat ) {
	      indexedLib[cat.name] = cat;
	    });
			allCats = [];
			$.each(indexedLib, function( index, box ) {
	      allCats.push(box);
	    });

			$('#addCat, #editCat, #selCat').empty();
	    $.each(allCats, function(index,cat){
	      $('#addCat,#editCat,#selCat').append(('<option value="'+index+'">'+cat.name+'</option>'));
	    });

			console.log('BUILD MERGED LIB');
			buildLibrary();
			// saveLibrary();    #TODO check if it's really necessary

		}





    ////////////////////////// MEDIAS ////////////////////////////////
		audioFiles = ['no media'];
		videoFiles = ['no media'];
		txtFiles = ['no media'];

		$.ajax({
			type: 'GET',
			timeout: 1000,
			url : urlbase+"/medialist",
			dataType: "jsonp"
		}).done(function(data) {
			audioFiles = data.audio;
			if (audioFiles.length>0) audioFiles.unshift(' ');
			else audioFiles = ['no media'];
			videoFiles = data.video;
			if (videoFiles.length>0) videoFiles.unshift(' ');
			else videoFiles = ['no media'];
		});

		$.ajax({
				url: "data/fileList.php",
				type: "POST",
				data: { type: 'text'}
		})
		.done(function(filelist) {
			txtFiles = [];
			if( Object.prototype.toString.call( filelist ) !== '[object Array]' ) {
				filelist = JSON.parse(filelist);
			}
			$.each(filelist,function(index,name){
					txtFiles.push(name.replace('.json',''));
			});
			if (txtFiles.length>0) txtFiles.unshift(' ');
			else txtFiles = ['no media'];
			console.log(txtFiles);
		});


		///////////////////////////TEXT FILES///////////////////////////////
    ///////////////////////////////////////////////////////////////////
    ///////////////////////////////////////////////////////////////////

		function textfile() {

			this.name = 'titreurs';

			this.loadText = function(title){
				if (title !== undefined) this.name = title;
				$('#titleTxtedit').text(this.name);
				console.log('LOADING TEXT '+this.name);
				$('#txted').hide();
				$.ajax({
						url: "data/load.php",
						dataType: "json",
						type: "POST",
						data: { filename: this.name, type: 'text'}
				})
				.done(function(reponse) {
						$('#txted').val(JSON.parse(reponse.contents).text);
						$('#txted').fadeIn(200);
				});
			}

			this.saveText = function (title){
				var contenu = $('#txted').val();
				title = $.trim(title).replace(/ /g,'_');
				this.name = title;
				if (title)
					$.ajax({
							url: "data/save.php",
							dataType: "json",
							type: "POST",
							data: {
								filename: title,
								type: 'text',
								timestamp: $.now(),
								contents: JSON.stringify({'text': contenu})
							}
					})
					.done(function() {
						$('#serverDisplay').html( 'Saved TXT : <br> '+ JSON.stringify({'text': contenu}) );
						textFile.loadText();

						// new file: refresh boxes
						if (txtFiles.indexOf(textFile.name) == -1) {
							txtFiles.push(textFile.name);
							$.each(allStates, function(index, state) {
								if (state.category == 'TITREUR')
									$(state.mediasList).append(('<option value="'+textFile.name+'">'+textFile.name+'</option>'));
								if (state.active) {
									$(state.mediasList).val(textFile.name);
									state.media = textFile.name;
								}
							})
						}

					});
			}
		}

		var textFile = new textfile();
		$('#okTxtedit').click(function(){
			var title = '';
			$.each(allStates, function(index, state) {
				if (state.active && state.category == 'TITREUR') title = state.media;
			});
			title = prompt("Text file name: ", title);
			textFile.saveText(title);
			//$('#editText').hide();
		});
		$('#cancelTxtedit').click(function(){
			//$('#editText').hide();
		});




    ///////////////////////////NEW STATE///////////////////////////////
    ///////////////////////////////////////////////////////////////////
    ///////////////////////////////////////////////////////////////////
		var relX=0;
		var relY=0;
    function draggable(){
    var draggablePos;
    $(".lib").draggable({
      start: function (e) {
        draggablePos = $(this).offset();
				  var parentOffset = $(this).offset();
					relX = e.pageX - parentOffset.left;
					relY = e.pageY - parentOffset.top;
        },
      stop: function (e,ui) {
          $(this).offset(draggablePos);
          if ((e.pageX < 900)&&(e.pageY < 3900)){

						////// FILL counter technique
						boxCount++;
						var counts = new Array();
						$.each(allStates,function(index,state){
							var count = state.boxname.replace('box','');
							counts.push(count);
						});
						counts.sort(function(a, b){return a-b});
						$.each (counts, function(index,num){
							if (num == boxCount) { boxCount++;}
						});

            var name = $(this).attr('id');
            var category = $(this).attr('category');
            var boxname = 'box' + boxCount;
            var py = e.pageY-relY;
            var px = e.pageX-relX;
            var arg1 = 'arg1';
            var arg2 = 'arg2';
            var boxCreated;
            for (var i = 0, len = allBoxes.length; i < len; i++) {
                if ((allBoxes[i].name === name)&&(allBoxes[i].category === category)) { boxCreated = allBoxes[i];}
            }
            var dispoBOO = boxCreated.dispos;
            var dispositifs = ["Self"];
            var medias = boxCreated.medias;
            var args = {};
            $.each(boxCreated.arguments,function(index,arg){
              args[arg] = null;
            });
            allStates.push(new state(name,boxname,category,px,py,dispoBOO,dispositifs,medias,args) );

						if (autoConnect == true) connectLastElements();

            }
          }
    });
    }
    draggable();

		// CONNECT LAST ELEMENTS OPTION
		var autoConnect = false;
    $('#autoConnect').change(function(){
      autoConnect = $('#autoConnect').prop('checked');
    });

		function connectLastElements(){
			var lastOne = allStates[allStates.length-2];
			var newOne = allStates[allStates.length-1];
			jsPlumb.connect({source:lastOne.connect, target:newOne.boxname});
		}


		////////////////////////// STATE ARGUMENT //////////////////////////////
    /////////////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////

		function stateArg(name, value) {
			var thisArg = this;

			this.name = name;
			this.value = value;

			this.nameDiv = $('<div>').addClass('option').text(this.name).attr('id', this.name);
			this.valDiv = $('<div>').addClass('optionval').text(this.value);
			this.editDiv = $('<input>').attr('type', 'text').addClass('textOption');

			this.valDiv.dblclick(function(e) {
				$(this).text("");
				thisArg.nameDiv.append(thisArg.editDiv);
				thisArg.editDiv.val(thisArg.value);
				thisArg.editDiv.focus();

				thisArg.editDiv.focusout(function(e) {
					thisArg.value = thisArg.editDiv.val();
					thisArg.valDiv.text(thisArg.value);
					thisArg.editDiv.remove();
					editing = false;
				});

				listening = false;
				editing = true;
			});
		}


    ////////////////////////// STATE OBJECT//////////////////////////////
    /////////////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////
    function state(name,boxname,category,px,py,dispoBOO,dispositifs,mediaBOO,arguments){


      var thisState = this;
  		this.box = $('<div>').addClass('box').attr('id', boxname);
      this.connect = $('<div>').addClass('connect').attr('id', 'Connector_'+boxname);

  		this.title = $('<div>').addClass('title').text(name).attr('id', name);
      this.name = name;
			this.boxname = boxname;
      this.category = category;
      this.mediasBOO = mediaBOO;
      this.dispoBOO = dispoBOO;

      for (var i = 0, len = allCats.length; i < len; i++) {
          if (allCats[i].name === this.category) { this.color = allCats[i].color; }
      }
      this.box.css('background-color', '#'+this.color);
      this.active = false;
  		this.box.css({
  		  'top': py,
  		  'left': px
  		});


  		this.box.append(this.title);

      if (dispoBOO==true){
        var dispos = $('<div>').addClass('form-group');
        this.disposList = $('<select>').attr('id','disposList').attr('multiple','multiple').appendTo(dispos);
        this.box.append(this.disposList);
      }
      if(mediaBOO == true){
        this.mediasList = $('<select>').attr('id', this.name+'Medias').addClass('dropdownMedias');//.attr('dir','rtl');
        this.box.append(this.mediasList);
        var files = new Array();
        if(category == 'AUDIO') {files=audioFiles;}
        if(category == 'VIDEO') {files=videoFiles;}
				if(category == 'TITREUR') {files=txtFiles;}
				this.media = files[0];
        $.each(files, function(index,file){
					var shortFile = file.split(".")[0]
         $(thisState.mediasList).append(('<option value="'+file+'">'+shortFile+'</option>'));
        });
      }

			// LOAD ARGUMENTS

			this.argumentsList = new Array();
			var keys = Object.keys(arguments), i, len = keys.length;
			keys.sort();
			for (i = 0; i < keys.length; i++) {
				var arg = new stateArg(keys[i], arguments[keys[i]]);
        thisState.argumentsList.push(arg);
				thisState.box.append(arg.nameDiv);
        thisState.box.append(arg.valDiv);
			}

  		this.box.append(this.connect);
  		$('#container').append(this.box);


      //////////////////////// DISPOS LIST /////////////////////
      if (dispoBOO==true){
        this.disposList.empty();
        this.disposList.append(('<option value="0">Self</option>'));
        this.disposList.append(('<option value="1">Group</option>'));
        this.disposList.append(('<option value="2">All</option>'));
        $.each(allPi, function(index,pi){
          var newIndex=index+3;
          thisState.disposList.append(('<option value="'+newIndex+'">'+pi.name+'</option>'));
        });
        this.disposList.multipleSelect({multipleWidth: 200, width: '100%',selectAll: false, countSelected: false});
        this.disposList.multipleSelect('refresh');

        this.dispositifs = dispositifs;

        this.disposList.change(function() {
          var that = $(this);
          thisState.dispositifs  = that.multipleSelect("getSelects","text");
          // Remove White space in disp name
           for (var i = 0, l = thisState.dispositifs.length; i < l; ++i) {
          thisState.dispositifs[i] = $.trim(thisState.dispositifs[i]);
          }
        });

        this.recheckDispos = function(){
          var toCheck = new Array();
          $.each(this.dispositifs, function(index,disp){
            if (disp === 'Self'){ toCheck.push(0);}
            if (disp === 'Group'){ toCheck.push(1);}
            if (disp === 'All'){ toCheck.push(2);}
            $.each(allPi, function(key,pi){
              if (disp === pi.name){actuKey = key+3; toCheck.push(actuKey);}
            });
          });
          thisState.disposList.multipleSelect("setSelects", toCheck);
        }
        this.recheckDispos();
      }


      this.sourceAndtarget = function (){
    		jsPlumb.makeTarget(thisState.box, {
    		  anchor: 'Continuous',
          //connector:"Straight",
                        //endpoint:[ "Rectangle", { width:0.1, height:0.1 }],
												endpoint:"Blank",
                        paintStyle:{ fillStyle:"dimgray", outlineColor:"dimgray", outlineWidth:2 },
                        hoverPaintStyle:{ fillStyle:"white" },
                        ConnectionOverlays: [ [ "Label", { label: "FOO", id: "label", cssClass: "aLabel" }]]
    		});
    		jsPlumb.makeSource(thisState.connect, {
    		  parent: thisState.box,
          anchor: "Continuous",
          //connector:"Straight",
					connector: [ "Flowchart", { stub: [0, 6], gap: 0, cornerRadius: 0, alwaysRespectStubs: false } ],

                endpoint:"Blank",
                connectorStyle:{ strokeStyle:"dimgray", lineWidth:2 },
                connectorHoverStyle:{ lineWidth:4 },
                ConnectionOverlays: [ [ "Label", { label: "FOO", id: "label", cssClass: "aLabel", fillStyle: "white" }]]
    		});
      }

  		jsPlumb.draggable(this.box, {
  		  containment: 'parent'
  		});

      this.sourceAndtarget();


      //////////////////////////  ARGUMENTS //////////////////////////////
      ///////////////////////////////////////////////////////////////////
      if(mediaBOO == true){
        $(thisState.mediasList).change(function(){
          var that = $(this);
          thisState.media = $(this).find('option:selected').val();
					thisState.mediasList.blur();
					if (thisState.category == 'TITREUR'){ textFile.loadText(thisState.media);}
        });
      }

      this.recoverInfos = function(media){
        $(thisState.mediasList).val(media);
				thisState.media = media;
      }


      this.resetColor = function(){
        this.box.css('background-color','#'+this.color);
      }

			this.select = function(){
				$('#editText').hide();

        $.each(allStates, function(index, state){
          state.active = false;
					this.resetColor();
        });
        this.active = true;
				selected='box';
        connectionSelected = null;
        listening = true;
        unselectConnections();

        this.box.css('background-color','lawngreen');
        if (autoConnect == false) $("#signalEdit").hide();

				if (this.category == 'TITREUR' && mediaBOO == true){
					$('#editText').fadeIn(200);
					textFile.loadText(thisState.media);
				}
			}
			//this.select();

  		this.box.click(function(e) {
				thisState.select();
  		});

			//REPAINT ??
			//jsPlumb.repaint(thisState.box);
			//jsPlumb.recalculateOffsets(thisState.box)

	  }
    /////////////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////



    ///////////////////////  CONNECTION /////////////////////////////////
    /////////////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////

		selectConnection = function(connection){
			selected = 'connection';
      connectionSelected = connection;
      $.each(allStates, function(index, state){
        state.active = false;
      });
			$('#editText').hide();
      var label = connectionSelected.getLabel();
			$("#signalEdit").fadeIn(400);

			//Actu selector
			$('#signalselector').val(
				$('#signalselector option').filter(function(){ return $(this).html() == label; }).val()
			);
			//Actu raccourci
			var indexlist = parseInt($('#signalselector option:selected').val())+65;
			$("#hotkey").html("Raccourci: alt+"+String.fromCharCode(indexlist)+"");


			$("#signalselector").change(function(){
				//show hotkey
				var indexlist = parseInt($('#signalselector option:selected').val())+65;
				$("#hotkey").html("Raccourci: alt+"+String.fromCharCode(indexlist)+"");
				//set label
				var newval = $('#signalselector option:selected').text();
				connectionSelected.setLabel(newval);
			});
      $("#signalName").val('Enter New...');

      //Style
      $.each(allStates, function(index, state){
        this.resetColor();
      });
	    unselectConnections();
      connection.setType("selected");
      if (label !== null) connection.setLabel(label);

		}

		//Shortcuts
		$(document).keyup(function(e){
		  if((e.altKey)&&(selected=='connection')&&(connectionSelected != null)){
					if((e.keyCode >= 65)&&(e.keyCode <= 91)){
						var touche = e.keyCode-65;
						console.log(touche);
						$("#signalselector option:eq("+touche+")").prop("selected", true);
						//$("#signalselector option:eq("+touche+")").attr('selected', 'selected');// don't work in firefox !
						//Actu raccourci, only si ca correspond à une option du signalselector
						var length = $('#signalselector').children('option').length;
						if (touche < length){ $("#hotkey").html("Raccourci: alt+"+String.fromCharCode(e.keyCode)+""); }
					}
					var newval = $('#signalselector option:selected').text();
					connectionSelected.setLabel(newval);
		   }
		});


    jsPlumb.bind("connection", function (info) {
				var Z = "dededede";
				info.connection.setLabel(Z);
				info.connection.setType("generic");
				selectConnection(info.connection);
    });

    jsPlumb.bind("click", function(connection) {
			selectConnection(connection);
    });


    $("#signalName").keyup(function(e) {
      listening = false;
		  if (e.keyCode == 13) {
				var newval = $("#signalName").val();
  			connectionSelected.setLabel(newval);
        connectionSelected.id=newval;
        listening = true;
				$("#signalEdit").hide();
				//Add new one ds la liste des signaux
				allSignals.push(newval);
				updateSignals();

		  }
		});


    function unselectConnections(){
      $.each(jsPlumb.getAllConnections(), function(idx, connection) {
        var label = connection.getLabel();
        connection.setType("generic");
        if (label !== null) connection.setLabel(label);
      });
    }

		var selected;
    /////////////////  DELETE  /////////////////
     $(document).keyup(function(e){

        if((e.keyCode == 8)&&(listening == true)&&(connectionSelected != null)&&(selected=='connection')&&(!textEditing) ){ ////del : 8 , - : 189
          e.preventDefault();
          jsPlumb.detach(connectionSelected);
          $("#signalEdit").hide();
					selected = 'nothing';
        }

        if((e.keyCode == 8)&&(listening == true)&&(selected=='box')&&(editing == false)&&(!textEditing)){
          e.preventDefault();
          var indextoremove;
          $.each(allStates, function(index, state) {
            if (state.active) {
              indextoremove = index;
              jsPlumb.detachAllConnections(state.box);
							jsPlumb.removeAllEndpoints(state.box);
              state.box.remove();
            }
          });
          allStates.splice(indextoremove,1);
					selected = 'nothing';
        }

    });

	    /////////////////////////////////////////////////////////////////////
	    /////////////////////////////////////////////////////////////////////


			unselectAll = function(){
				$.each(allStates, function(index, state){
					state.active = false;
					state.box.css('background-color','#'+state.color);
				});
				state. active = true;
				selected='nothing';
				connectionSelected = null;
				listening = false;
				unselectConnections();
			}








    ///////////// BACKSPACE NOT GOING BACKWARD /////////////////
		textEditing = false;

    window.addEventListener('keydown', function (e) {
        if (e.keyIdentifier == 'U+0008' || e.keyIdentifier == 'Backspace' || e.keyCode == 8 || document.activeElement != 'text')
          {
            if (e.target === document.body) { e.preventDefault(); }
          }
    }, true);

		$("textarea").on("focusin", function(e){
		  textEditing = true;
		});

		$("textarea").on("focusout", function(e){
		  textEditing = false;
		});


   /////////////////////// CLEAR /////////////////////////
    $('#clearGraph').click( function() {
      clearAll();
    });

    function clearAll(){


			jsPlumb.detachEveryConnection();
      $('.box').remove();
      allStates = [];

			//jsPlumb.reset();
			// AND REPAINT EVERYTHING AFTER LOAD?
			//jsPlumb.repaintEverything();
    }



    ///////////////////////////   SAVE   ////////////////////////////////
    /////////////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////
		var doReload = false;


    function saveGraphique(){
      var boxes = [];

      $.each(allStates, function(index, state) {

      var $box = $(state.box);
			var argArray = {};
			$.each(state.argumentsList, function(index, arg) {
				argArray[arg.name] = arg.value;
			});

			var allArgs = $.extend({}, argArray, {media : state.media, dest: state.dispositifs });



      boxes.push({
        name: state.name,
        boxname: $box.attr('id'),
        category: state.category,
        positionX: parseInt($box.css("left"), 10),
        positionY: parseInt($box.css("top"), 10),
        dispoBOO: state.dispoBOO,
        dispositifs: state.dispositifs,
        media: state.media,
        arguments: argArray,
				allArgs : allArgs
        });
      });

      var connections = [];
      $.each(jsPlumb.getConnections(), function (index, connection) {
        connections.push({
          //connectionId: connection.id,
					connectionLabel: connection.getLabel(),
          From:$("#"+connection.sourceId).parent().children(".title").attr("id"),
          To: $("#"+connection.targetId).children(".title").attr("id"),
          // on retrouve le state.name (ou le title.attr('id')) de SourceId et TargetId,
          //car si on change les id's au changement du state.name, les connexions perdent leur ancrages
          // --> Une fois une connection faite on ne peut plus changer les id's des box
          SourceId: connection.sourceId,
          TargetId: connection.targetId
        });
      });


			var sources = [];
			var targets = [];
			$.each(jsPlumb.getConnections(), function (index, connection) {
				sources.push( connection.sourceId.replace('Connector_', '') );
				targets.push(connection.targetId);
      });
			var origins = $(sources).not(targets).get();
			var uniqueOrigins = [];
			$.each(origins, function(i, el){
			    if($.inArray(el, uniqueOrigins) === -1) uniqueOrigins.push(el);
			});

      Graphique.boxes = boxes;
      Graphique.connections = connections;
			Graphique.origins = uniqueOrigins;



    }

    $('#saveGraph').click( function() {
				if (scenarioName == '') return;
				saveGraphique();
        $.ajax({
            url: "data/save.php",
            dataType: "json",
            type: "POST",
            data: {
                contents: JSON.stringify(Graphique),
                filename: scenarioName,
								timestamp: $.now(),
								type: 'scenario'
            }
        })
        .done(function(reponse)
        {
            if (reponse.status == 'success')
            {
							$('#serverDisplay').html( 'Saved : <br> '+ JSON.stringify(Graphique) );
							if (doReload) {
								window.open(window.location.href.split("#")[0]+'#'+timelineName+'#'+scenarioName,"_self");
								location.reload(true);
							}
							else timelineInfo();
						}
        })
        .fail(function()
          { $('#serverDisplay').html( 'Impossible de joindre le serveur...' ); }
        );

    });

		$('#saveAsGraph').click( function() {
			var newName = prompt("Save timeline as", scenarioName);
			if (newName != null) {
				scenarioName = newName;
				doReload = true;
				$('#saveGraph').click();
			}
		});

		$('#sendGraph').click( function() {
			$.ajax({
					url: "data/send_version.php",
					type: "POST"
				}
			).done(function(r){
				$('#serverDisplay').html("SEND !");
			});
		});
		
		$('#restartBtn').click( function() {
			$.ajax({
					url: "data/restart.php",
					type: "POST"
				}
			).done(function(r){
				$('#serverDisplay').html("RESTART !");
			});
		});

		$('#delGraph').click( function() {
		if (confirm("Delete "+scenarioName+" ?")) {
				$.ajax({
						url: "data/fileDelete.php",
						type: "POST",
						data: {
								filename: scenarioName,
								type: 'scenario'
						}
				})
				.done(function(reponse) {
						if (reponse.status == 'success') {
							var url = window.location.href.split("#")[0]+'#'+timelineName;
							window.location.replace(url);
							location.reload();
						}
						else if (reponse.status == 'error')
							$('#serverDisplay').html( 'Erreur serveur: '+reponse.message );
				})
				.fail(function() { $('#serverDisplay').html( 'Impossible de joindre le serveur...' ); } );

			}
		});

    ///////////////////////////   LOAD   ////////////////////////////////
    /////////////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////
    $('#loadGraph').click( function() {
      loadScenario();
    });

    function loadScenario() {
			console.log("loading Scenario");
	    $.ajax({
	        url: "data/load.php",
	        dataType: "json",
	        type: "POST",
	        data: {
	            filename: scenarioName,
							type: 'scenario'
	        }
	    })
	    .done(function(reponse) {
	        if (reponse.status == 'success')
	        {
	            $('#serverDisplay').html('Loaded: <br>' + reponse.contents );
	            Graphique = JSON.parse(reponse.contents);
							if (loadGraphAfter == true) { loadGraphique(); }
	        }
	        else if (reponse.status == 'error')
	        { $('#serverDisplay').html( 'Erreur côté serveur: '+reponse.message ); }
	    })
	    .fail(function() {
	        $('#serverDisplay').html( 'Impossible de joindre le serveur...' );
	    });
    }

    function loadGraphique(){
      clearAll();
			//jsPlumb.reset();
			console.log("loading Graph");

      var boxes = Graphique.boxes;
      $.each(boxes, function( index, box ) {
        var mediaBOO;
        if (box.media) mediaBOO = true;
        allStates.push(new state(box.name, box.boxname, box.category, box.positionX, box.positionY, box.dispoBOO, box.dispositifs, mediaBOO, box.arguments) );
      });

      $.each(allStates, function( index, state ) {
        if(boxes[index].media != null) {
          state.recoverInfos(boxes[index].media);
          }
      });

      var connections = Graphique.connections;
      $.each(connections, function( index, connection ) {
         var newConnection = jsPlumb.connect({
            source: connection.SourceId,
            target: connection.TargetId
            //anchors: ["BottomCenter", [0.75, 0, 0, -1]]
        });
				if (connection.connectionLabel !== null) {newConnection.setLabel(connection.connectionLabel);}
				// Si signal pas dans lib, l'ajouter au dropdown
				if($.inArray(connection.connectionLabel, allSignals)===-1){allSignals.push(connection.connectionLabel);}
				updateSignals();
      });

			unselectAll();
			$("#signalEdit").hide();

			//jsPlumb.repaintEverything();
			// $.each(allStates, function( index, state ) {
			// 			jsPlumb.repaint(state.box);
			// 			jsPlumb.recalculateOffsets(state.box)
			// });



    }


    ///////////////////////////   TIMELINE   ////////////////////////////
    /////////////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////
    var vars = window.location.hash.substr(1);
    if (vars == '') {
			vars = 'timeline#noscenario';
		}
    var variables = vars.split('#');
    var timelineName = variables[0];
    var scenarioName = variables[1];

    var poolImport = {};
    var allPi = {};

    function loadTimeline(){
      $.ajax({
          url: "../_TIMELINE/data/load.php",
          dataType: "json",
          type: "POST",
          data: {
              filename: timelineName,
							type: 'timeline'
          }
      })
      .done(function(reponse) {
          if (reponse.status == 'success')
          {
              poolImport = JSON.parse(reponse.contents);
              allPi = poolImport.pool;
          }
      });

    }


    //////////////////////// CHOOSE  SCENARIO   /////////////////////////
    /////////////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////
		var loadGraphAfter = false;
		var allScenarios = [];
		function loadScenariosList(){
      allScenarios = [];
      $.ajax({
          url: "data/fileList.php",
					type: "POST",
          data: { type: 'scenario'}
      })
      .done(function(filelist) {
        var scenariosList = filelist;
        if( Object.prototype.toString.call( scenariosList ) !== '[object Array]' ) {
          scenariosList = JSON.parse(scenariosList);
        }
        $.each(scenariosList,function(index,name){
          if (name !== 'library.json'){
            var newname = name.replace('.json','');
            allScenarios.push(newname);
          }
        });
				$('#selFile').empty();
				$.each(allScenarios, function(index,scenario){
					$('#selFile').append(('<option value="'+scenario+'">'+scenario+'</option>'));
				});
				$('#selFile').val(scenarioName);
      });
    }

		$('#selFile').change(function(){
			scenarioName = $('#selFile option:selected').text();
			window.open(window.location.href.split("#")[0]+'#'+timelineName+'#'+scenarioName,"_self");
			location.reload(true);
			// loadGraphAfter = true;
			// loadScenario();
		});
		document.title = scenarioName;



    ///////////////////////////   START   ////////////////////////////
		loadScenariosList();
    loadTimeline();
		//loadScenario();

		loadGraphAfter = true;

    $(".textarea").on("click", function () {
      $(this).select();
    });

		//////////////////////// GET NAME TIMELINE .///////////////////////

		var shadow_edit = false;
    $('#toggle_shadowedit').change(function(){
      $.ajax({
          url: "data/shadow_edit.php",
          type: "POST",
          data: { shadow_edit: $('#toggle_shadowedit').prop('checked')}
      }).done(function(reponse) {
        shadow_edit = $('#toggle_shadowedit').prop('checked');
  		});
    });

		function timelineInfo() {
      $.ajax({
          url: "/info",
          dataType: "json"
      })
      .done(function(r) {
        $("#timeline_group").text(r.timeline.group);
          $("#timeline_version").html("<br />"+r.timeline.version+" UTC+0");
        if(r.timeline.shadow_edit){
          $('#toggle_shadowedit')[0].checked = true;
        }
      });
    }
    timelineInfo();





		//if (scenarioName !== 'noscenario') { console.log(scenarioName); setTimeout(loadGraphique, 200); }

		// $(document).ajaxStop(function(){
		// 	if (scenarioName !== 'noscenario') { loadGraphique(); }
		// });



	});
