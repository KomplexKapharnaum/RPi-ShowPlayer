	jsPlumb.ready(function() {

    /////////////////////////  GLOBAL  //////////////////////////////

    jsPlumb.registerConnectionType("selected", {
      paintStyle:{ strokeStyle:"lawngreen", lineWidth:3  },
      hoverPaintStyle:{ strokeStyle:"lawngreen", lineWidth:4 },
      ConnectionOverlays: [ [ "Label", { label: "FOO", id: "label", cssClass: "aLabel" }]]
    });

    jsPlumb.registerConnectionType("generic", {
      paintStyle:{ strokeStyle:"dimgray", lineWidth:3  },
      hoverPaintStyle:{ strokeStyle:"dimgray", lineWidth:4 },
      ConnectionOverlays: [ [ "Label", { label: "FOO", id: "label", cssClass: "aLabel" }]]
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
		//var

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
			  url: "http://2.0.1.89:8080/library",
				dataType: "jsonp",
			}).done(function(data) {
				hardlib = data.functions;
				mergeLibrary();
				allSignals = data.signals;
				updateSignals();
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
			saveLibrary();

		}





    ////////////////////////// MEDIAS ////////////////////////////////
		audioFiles = ['select...','son1','son2','son3','son4'];
		videoFiles = ['select...','vid1','vid2','vid3','vid4'];
		txtFiles = ['select...','text1','text2','text3','text4'];
		$.ajax({
			type: 'GET',
			timeout: 1000,
		  url: "http://2.0.1.89:8080/medialist",
			dataType: "jsonp",
		}).done(function(data) {
			audioFiles = data.audio;
			audioFiles.unshift('Select...');
			videoFiles = data.video;
			videoFiles.unshift('Select...');
			txtFiles = data.txt;
			txtFiles.unshift('Select...');
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
          if ((e.pageX < 900)&&(e.pageY < 2000)){

						boxCount++;
						$.each(allStates,function(index,state){
							var count = state.boxname.replace('box','');
							if (count == boxCount) { boxCount++; }
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
            }
          }
    });
    }
    draggable();




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

      this.argumentsArray = arguments;
      this.argumentsList = new Array();
      var k = 0;
      $.each(this.argumentsArray,function(name,val){
        thisState.argumentsList[k++] = name;
      })

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
        this.media = 'Select...';
        this.mediasList = $('<select>').attr('id', this.name+'Medias').addClass('dropdownMedias')
        this.box.append(this.mediasList);
        var files = new Array();
        if(category == 'AUDIO') {files=audioFiles;}
        if(category == 'VIDEO') {files=videoFiles;}
				if(category == 'TITREUR') {files=txtFiles;}
        $.each(files, function(index,file){
         $(thisState.mediasList).append(('<option value="'+file+'">'+file+'</option>'));
        });
      }
      if(this.argumentsList[0]){
        this.arg1Name = $('<div>').addClass('option').text(thisState.argumentsList[0]).attr('id', thisState.argumentsList[0]);
        this.arg1Val = $('<div>').addClass('optionval').text(thisState.argumentsArray[thisState.argumentsList[0]]);
        this.box.append(this.arg1Name);
        this.box.append(this.arg1Val);
      }
      if(this.argumentsList[1]){
        this.arg2Name = $('<div>').addClass('option').text(thisState.argumentsList[1]).attr('id', thisState.argumentsList[1]);
        this.arg2Val = $('<div>').addClass('optionval').text(thisState.argumentsArray[thisState.argumentsList[1]]);
        this.box.append(this.arg2Name);
        this.box.append(this.arg2Val);
      }
      if(this.argumentsList[2]){
        this.arg3Name = $('<div>').addClass('option').text(thisState.argumentsList[2]).attr('id', thisState.argumentsList[2]);
        this.arg3Val = $('<div>').addClass('optionval').text(thisState.argumentsArray[thisState.argumentsList[2]]);
        this.box.append(this.arg3Name);
        this.box.append(this.arg3Val);
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
                        endpoint:[ "Rectangle", { width:10, height:10 }],
                        paintStyle:{ fillStyle:"dimgray", outlineColor:"dimgray", outlineWidth:2 },
                        hoverPaintStyle:{ fillStyle:"white" },
                        ConnectionOverlays: [ [ "Label", { label: "FOO", id: "label", cssClass: "aLabel" }]]
    		});
    		jsPlumb.makeSource(thisState.connect, {
    		  parent: thisState.box,
          anchor: "Continuous",
          //connector:"Straight",
					connector: [ "Flowchart", { stub: [0, 6], gap: 2, cornerRadius: 0, alwaysRespectStubs: false } ],

                endpoint:"Blank",
                connectorStyle:{ strokeStyle:"dimgray", lineWidth:3 },
                connectorHoverStyle:{ lineWidth:4 },
                ConnectionOverlays: [ [ "Label", { label: "FOO", id: "label", cssClass: "aLabel", fillStyle: "white" }]]
    		});
      }

  		jsPlumb.draggable(this.box, {
  		  containment: 'parent'
  		});

      this.sourceAndtarget();

  		this.box.click(function(e) {
				$('#editText').hide();

        $.each(allStates, function(index, state){
          state.active = false;
					this.resetColor();
        });
        thisState. active = true;
				selected='box';
        connectionSelected = null;
        listening = true;
        unselectConnections();

        thisState.box.css('background-color','lawngreen');
        $("#signalEdit").hide();

				if (thisState.category == 'TITREUR' && mediaBOO == true){
					 console.log('loading txt...');
					$('#editText').fadeIn(200);
					console.log ('titreur Edit');
					thisState.loadText();
					}


  		});

			this.loadText = function(){
				console.log('LOADING TEXT'+thisState.media);
        $.ajax({
            url: "data/loadText.php",
            dataType: "json",
            type: "POST",
            data: { filename: thisState.media, type: 'text'}
        })
        .done(function(reponse) {
            if (reponse.status == 'success') { $('#txted').text(reponse.contents); }
        });
			}

			this.saveText = function (){
				var contenu = $('#txted').val();
				$.ajax({
            url: "data/saveText.php",
            dataType: "json",
            type: "POST",
            data: { filename: thisState.media, type: 'text', contents: contenu }
        });
			}

			$('#okTxtedit').click(function(){
				if (thisState.category == 'TITREUR' && mediaBOO == true){
					thisState.saveText();
				}
				$('#editText').hide();
			});
			$('#cancelTxtedit').click(function(){
				$('#editText').hide();
			});



      //////////////////////////  ARGUMENTS //////////////////////////////
      ///////////////////////////////////////////////////////////////////
      if(mediaBOO == true){
        $(thisState.mediasList).change(function(){
          var that = $(this);
          thisState.media = $(this).find('option:selected').text();
					if (thisState.category == 'TITREUR'){ thisState.loadText();}
        });
      }

      if(this.argumentsList[0]){
        var arg1Temp = $('<input>').attr('type', 'text').addClass('textOption');
        this.arg1Val.dblclick(function(e) {
          $(this).text("");
          thisState.arg1Name.append(arg1Temp);
					arg1Temp.val(thisState.argumentsArray[thisState.argumentsList[0]]);
          arg1Temp.focus();
          listenToEnterArg1();
          listening = false;
					editing = true;
        });
        function listenToEnterArg1(){
          arg1Temp.focusout(function(e) {
            thisState.arg1Val.text(this.value);
            thisState.arg1Val.attr('id', this.value);
            thisState.argumentsArray[thisState.argumentsList[0]]=this.value;
            arg1Temp.remove();
						editing = false;
          });
        }
      }
      if(this.argumentsList[1]){
        var arg2Temp = $('<input>').attr('type', 'text').addClass('textOption');
        this.arg2Val.dblclick(function(e) {
          $(this).text("");
          thisState.arg2Name.append(arg2Temp);
					arg2Temp.val(thisState.argumentsArray[thisState.argumentsList[1]]);
          arg2Temp.focus();
          listenToEnterArg2();
          listening = false;
					editing = true;
        });
        function listenToEnterArg2(){
          arg2Temp.focusout(function(e) {
            thisState.arg2Val.text(this.value);
            thisState.arg2Val.attr('id', this.value);
            thisState.argumentsArray[thisState.argumentsList[1]]=this.value;
            arg2Temp.remove();
						editing = false;
          });
        }
      }
      if(this.argumentsList[2]){
        var arg3Temp = $('<input>').attr('type', 'text').addClass('textOption');
        this.arg3Val.dblclick(function(e) {
          $(this).text("");
          thisState.arg3Name.append(arg3Temp);
					arg3Temp.val(thisState.argumentsArray[thisState.argumentsList[2]]);
          arg3Temp.focus();
          listenToEnterArg3();
          listening = false;
					editing = true;
        });
        function listenToEnterArg3(){
          arg3Temp.focusout(function(e) {
            thisState.arg3Val.text(this.value);
            thisState.arg3Val.attr('id', this.value);
            thisState.argumentsArray[thisState.argumentsList[2]]=this.value;
            arg3Temp.remove();
						editing = false;
          });
        }
      }

      this.recoverInfos = function(media){
        $(thisState.mediasList).val(media);
				thisState.media = media;
      }


      this.resetColor = function(){
        this.box.css('background-color','#'+this.color);
      }

			//REPAINT ??
			//jsPlumb.repaint(thisState.box);
			//jsPlumb.recalculateOffsets(thisState.box)

	  }
    /////////////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////








    ///////////////////////  CONNECTION /////////////////////////////////
    /////////////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////


    jsPlumb.bind("connection", function (info) {
        //info.connection.setLabel(info.connection.id);
				info.connection.setLabel('');

    });


    jsPlumb.bind("click", function(connection) {
			selected = 'connection';
      connectionSelected = connection;
      $.each(allStates, function(index, state){
        state.active = false;
      });
			$('#editText').hide();
      var label = connectionSelected.getLabel();
			$("#signalEdit").fadeIn(400);

			$('#signalselector').val(
				$('#signalselector option').filter(function(){ return $(this).html() == label; }).val()
			);

			$("#signalselector").change(function(){
				var newval = $('#signalselector option:selected').text();
				connectionSelected.setLabel(newval);
				//connectionSelected.id=newval;
			});

      $("#signalName").val('Enter New...');
			//$("#signalName").focus();

      $("#signalName").keyup(function(e) {
			//$("#signalName").focusout(function(e) {
        listening = false;
  		  if (e.keyCode == 13) {
					var newval = $("#signalName").val();
    			connectionSelected.setLabel(newval);
          connectionSelected.id=newval;
          listening = true;
					$("#signalEdit").hide();
  		  }
  		});
      //Style
      unselectConnections();
      connection.setType("selected");
      connection.setLabel(label);
      $.each(allStates, function(index, state){
        this.resetColor();
      });

    });


    function unselectConnections(){
      $.each(jsPlumb.getAllConnections(), function(idx, connection) {
        var label = connection.getLabel();
        connection.setType("generic");
        connection.setLabel(label);
      });
    }

		var selected;
    /////////////////  DELETE  /////////////////
     $(document).keyup(function(e){

        if((e.keyCode == 8)&&(listening == true)&&(connectionSelected != null)&&(selected=='connection') ){ ////del : 8 , - : 189
          e.preventDefault();
          jsPlumb.detach(connectionSelected);
          $("#signalEdit").hide();
					selected = 'nothing';
        }

        if((e.keyCode == 8)&&(listening == true)&&(selected=='box')&&(editing == false)){
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

    window.addEventListener('keydown', function (e) {
        if (e.keyIdentifier === 'U+0008' || e.keyIdentifier === 'Backspace' || e.keyCode === '8' || document.activeElement !== 'text')
          {
            if (e.target === document.body) { e.preventDefault(); }
          }
    }, true);


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

    function saveGraphique(){
      var boxes = [];

      $.each(allStates, function(index, state) {

      var $box = $(state.box);
			var allArgs = $.extend({}, state.argumentsArray, {media : state.media, dest: state.dispositifs });


      boxes.push({
        name: state.name,
        boxname: $box.attr('id'),
        category: state.category,
        positionX: parseInt($box.css("left"), 10),
        positionY: parseInt($box.css("top"), 10),
        dispoBOO: state.dispoBOO,
        dispositifs: state.dispositifs,
        media: state.media,
        arguments: state.argumentsArray,
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
            {  $('#serverDisplay').html( 'Saved : <br> '+ JSON.stringify(Graphique) );  }
        })
        .fail(function()
          { $('#serverDisplay').html( 'Impossible de joindre le serveur...' ); }
        );

    });

    ///////////////////////////   LOAD   ////////////////////////////////
    /////////////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////
    $('#loadGraph').click( function() {
      loadScenario();
    });

    function loadScenario() {
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
        newConnection.setLabel(connection.connectionLabel);
      });

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
        var scenariosList = JSON.parse(filelist);
        $.each(scenariosList,function(index,name){
          if (name !== 'library.json'){
            var newname = name.replace('.json','');
            allScenarios.push(newname);
          }
        });
				$.each(allScenarios, function(index,scenario){
					$('#selFile').append(('<option value="'+scenario+'">'+scenario+'</option>'));
				});
				$('#selFile').val(scenarioName);
      });
    }

		$('#selFile').change(function(){
			scenarioName = $('#selFile option:selected').text();
			// window.open(window.location.href+'#timeline#'+scenarioName,"_self");
			// location.reload(true);
			loadGraphAfter = true;
			loadScenario();
		});



    ///////////////////////////   START   ////////////////////////////
		loadScenariosList();
    loadTimeline();
		loadScenario();

		loadGraphAfter = true;


		if (scenarioName !== 'noscenario') { setTimeout(loadGraphique, 200); }

		// $(document).ajaxStop(function(){
		// 	if (scenarioName !== 'noscenario') { loadGraphique(); }
		// });



	});
