
    $(function() {

      //allPi = new Array();
      $('#colonne2').hide();
      setTimeout(function(){
        loadTimeline();
        $('#colonne2').fadeIn(200);
      },100);


      function pool() {

        allPi = new Array();
        var lineCount = 0;


        this.unselectBlocks = function() {
          $.each(allPi, function(index, pi) {
            pi.unselectBlocks();
          });
        };

        this.selectallBlocks = function() {
          $.each(allPi, function(index, pi) {
            pi.selectallBlocks();
          });
        };

        this.getActiveBlock = function() {
          var activeB = new Array();
          $.each(allPi, function(index, pi) {
            $.each(pi.getBlocks(), function(index, block) {
              if (block.active) activeB.push(block);
            });
          });
          return activeB;
        };

        this.unselectLines = function() {
          $.each(allPi, function(index, pi) {
            pi.active = false;
            pi.linename.css('backgroundColor', 'EEEEEE');
          });
        };

        this.getActivePi = function() {
          var activeL = new Array();
          $.each(allPi, function(index, pi) {
            if (pi.active) activeL.push(pi);
          });
          return activeL;
        };


        this.addPi = function() {
          lineCount++;
          allPi.push(new pi("Pi"+lineCount));
          //allPi.push(new pi(allPi.length)); // bug si mm id
          $("#piname").text("Select...");
          $("#disposms").multipleSelect("setSelects", 0);
        }

        this.addPiFromJson = function(name) {
          allPi.push(new pi(name));
        }

        this.delPi = function() {
          var indextoremove;
          $.each(allPi, function(index, pi) {
            if (pi.active) indextoremove = index;
          });
          allPi.splice(indextoremove,1);

        }
      }



      /////////////////////// PI OBJECT ////////////////////////
      //////////////////////////////////////////////////////////
      function pi(id) {


        //var allBlocks = new Array();
        this.allBlocks = new Array();
        //this.allBlocks = [];

        this.blockCount = 0;
        this.linename = $('<div>').addClass('linename').appendTo( $('#allpinames') );
        this.linename.hide().fadeIn(150);
        this.line = $('<div>').addClass('line').appendTo( $('#allpi') );
        this.line.hide().fadeIn(150);
        //this.line.attr('id', id);
        //this.line.removeClass('selected');

        this.raspiname = id;
        this.linename.text(this.raspiname);
        this.modules = new Array();
        pool.unselectLines();
        this.active = false;

        var thispi = this;



        this.line.dblclick( function()
        {
          //$("#scenariosms").multipleSelect("setSelects", 0);
          thispi.allBlocks.push(new block(thispi));
          $("#blocknameVisu").text("Select...");

        });


        $(this.line).on('click', function () {
          thispi.editInfos();
        });
        $(this.linename).on('click', function () {
          thispi.editInfos();
        });

        this.editInfos = function (){
          $("#piname").text(thispi.raspiname);
          pool.unselectLines();
          thispi.active = true;
          thispi.linename.css('backgroundColor', 'DDDDDD');
          var toCheck = new Array();
          $.each(thispi.modules, function(index,module){
             $.each(allModules,function(key,modulo){
               if (module === modulo){ toCheck.push(key);}
             });
          });
          $("#disposms").multipleSelect("setSelects", toCheck);
        }

        this.recoverPiInfos = function(mod){
          thispi.modules = mod;
        }

        ///////////////////NAME EDITOR /////////////////
        var piName = $('<input>').attr('type', 'text').addClass("textareaSmall");
        $(this.linename).on('dblclick', function (e) {
          $(this).text("");
          thispi.linename.append(piName);
          piName.val(thispi.raspiname);
          piName.focus();
          listenToEnter();
          e.stopPropagation();
          listening = false;
        });
        function listenToEnter(){
        piName.focusout(function(e) {
    			$(this).parent().text(this.value);
          thispi.raspiname = this.value;
          $("#piname").text(thispi.raspiname);
    		});
        }
        listenToEnter();
    		piName.focus();
        /////////////////////////////////////

        this.unselectBlocks = function() {
          $.each(thispi.allBlocks, function(index, block) {
            block.active = false;
            $(".block").css('opacity', '.5');
            //$(".block").css('background-image', 'none');
          });
        };

        this.selectallBlocks = function() {
          $.each(thispi.allBlocks, function(index, block) {
            block.active = true;
          });
        };

        this.getBlocks = function() {
          return thispi.allBlocks;
        }

        this.deleteLine = function(){
          this.line.remove();
          this.linename.remove();
          $.each(thispi.allBlocks, function(index, block) {
            block.keyframe_start.remove();
            block.keyframe_end.remove();
          });
        }

      }

      /////////////////////// BLOCK OBJECT ////////////////////////
      //////////////////////////////////////////////////////////
      function block(thispi) {

        thispi.blockCount++;
        var block = $('<div>').addClass('block');
        thispi.line.append(block);
        //block.hide().fadeIn(200); // marche la premiere fois seulement ??
        //block.appendTo(thispi.line).hide().fadeIn(200);

        this.blockName = "block" +thispi.blockCount;
        block.attr('id', this.blockName);


        this.scene = allScenes[0];

        this.scenarios = [];
        pool.unselectBlocks();
        this.active = true;
        $('#blocknameVisu').text(block.attr('id'));
        var thisblock = this;



        block.on('click', function () {
          pool.unselectBlocks();
          thisblock.active = true;
          thisblock.editInfos();
          $(this).css('opacity', '.9');//B5B5B5
          //$(this).css({'background-image':'url(noise.png)'});
        });


        this.editInfos = function(){
          console.log(this.scenarios);
          $('#blocknameVisu').text(block.attr('id'));
          var scenename = thisblock.scene.name;
          $('#sceneselector').val(
            $('#sceneselector option').filter(function(){ return $(this).html() == scenename; }).val()
          );
          var toCheck = new Array();
          $.each(this.scenarios, function(index,scenario){
            $.each(allScenarios, function(key,scenar){
              if (scenario === scenar.name) { toCheck.push(key);}
            });

          });
          $("#scenariosms").multipleSelect("setSelects", toCheck);
          }



        this.refreshInfos = function(){
          block.css('backgroundColor', thisblock.scene.color);
        }


        this.deleteElement = function(){
          var indextoremove;
          $.each(thispi.allBlocks, function(index, block) {
            if (block.active) indextoremove = index;
          });
          thispi.allBlocks.splice(indextoremove,1);
          block.remove();
          thisblock.keyframe_start.remove();
          thisblock.keyframe_end.remove();
          $.each(thispi.allBlocks, function(index, block) {
          block.keyframePosition();
          });
        }


        this.recoverInfos = function(infos){
          thisblock.name = infos.name;
          $(block).css({left:infos.start});
          $(block).width(infos.end-infos.start);
          if (block.prev().hasClass("block")) {
            var prev = block.prev();
            var prevwidth = prev.width();
            $(block).css({left:infos.start-prevwidth});
          }
          thisblock.keyframePosition();
          thisblock.scenarios = infos.scenarios;
          thisblock.scene = infos.scene;
          thisblock.refreshInfos();
        }

        //Move after prev (if prev is a block)
        if (block.prev().hasClass("block")) {
          var prev = block.prev();
          var blockpos = block.offset();
          var prevpos = prev.offset();
          var prevwidth = prev.width();///  outerWidth() if inner border
          blockpos.left = prevpos.left + prevwidth;
          block.offset(blockpos);
        }

        ///////////////////KEYFRAMES///////////////////////
        this.keyframe_start = $('<div>').addClass('key').appendTo( $('#allKeys') );
        this.keyframe_end = $('<div>').addClass('key').appendTo( $('#allKeys') );
        this.start = this.keyframe_start.offset();
        this.end = this.keyframe_end.offset();

        this.keyframePosition = function(){
          var w = $(block).width();///  outerWidth() if inner border
          var offset = $(block).offset();
          thisblock.start.left=offset.left;
          thisblock.keyframe_start.offset(thisblock.start);
          thisblock.end.left = offset.left + w;
          thisblock.keyframe_end.offset(thisblock.end);
        }
        this.keyframePosition();
        ////////////////////////////////////////////////////
        var resized = true;

        block.resizable({
          handles: "e",
          grid: 50,
          containment: "parent",
          resize: function() {
            thisblock.keyframePosition();
            $.each(thispi.allBlocks, function(index, block) {
            block.keyframePosition();
            });
            resized = false;
            setTimeout(function(){ resized = true },1000);
          }
        });
        block.draggable({
          grid: [ 50,50 ],
          axis: "x",
          containment: "parent",
          drag: function(){
            thisblock.keyframePosition();
          }
          });


        block.mouseenter(function(e){
          $('.tip').html('');
          $.each(thisblock.scenarios,function(index,scenar){
            $('.tip').append(scenar+'<br>');
          });
        });
        block.mousemove(function(e){
          //var blockpos = block.offset();
          //$('.tip').css({ 'top': blockpos.top+5,'left': blockpos.left+5 });
          if (resized == true && tooltips == true){
            $('.tip').show();
          }
          $('.tip').css({ 'top': e.pageY+25,'left': e.pageX-30 });
        });

        block.mouseout(function(){
          $('.tip').hide();
        });





      }

    //////////////////// DISPOSITIFS ///////////////////
      var allModules = ['MODULAUDIO','VIDEO','LIGHT','TITREUR','LI12','PB12','PB24'];

  		$.ajax({
  			type: 'GET',
  			timeout: 1000,
  		  url: "http://2.0.1.89:8080/moduleslist",
  			dataType: "jsonp",
  		}).done(function(data) {
        allModules = {};
  			allModules = data;
        refreshModulesList();
  		});


    //////////////////// SCENES ///////////////////
    var colors = new Array ('B5B5B5','218C8D','D83E3E','F9E559','EF7126','8EDC9D','A05C7B',
    'E1CE9A','3F7CAC','E21D1D','82A647','9B6236','75C1FF','C4E00F','F4FF52','6E0014');
      var scene0 = {name:'default', color:colors[0]};
      var scene1 = {name:'scene1', color:colors[1]};
      var scene2 = {name:'scene2', color:colors[2]};
      var scene3 = {name:'scene3', color:colors[3]};
      var scene4 = {name:'scene4', color:colors[4]};
      var scene5 = {name:'scene5', color:colors[5]};
      var scene6 = {name:'scene6', color:colors[6]};
      var scene7 = {name:'scene7', color:colors[7]};
      var allScenes = new Array();
      allScenes.push(scene0);
      allScenes.push(scene1);
      allScenes.push(scene2);
      allScenes.push(scene3);
      allScenes.push(scene4);
      allScenes.push(scene5);
      allScenes.push(scene6);
      allScenes.push(scene7);


    //////////////////// SCENARIOS ///////////////////
    var allScenarios = new Array();
    // var scenario1 = {name:'scenario1',active:false};
    // allScenarios.push(scenario1);
    function getScenarios(){
      allScenarios = [];
      $.ajax({
          url: "data/fileList.php",
          type: "POST",
          data: { type: 'scenario',
                  directory: '../../_SCENARIO/data'
          }
      })
      .done(function(filelist) {
        var scenariosList = JSON.parse(filelist);
        $.each(scenariosList,function(index,name){
          if (name !== 'library.json'){
            var newname = name.replace('.json','');
            var scenar = {name:newname,active:false};
            allScenarios.push(scenar);
          }
        });
        refreshscenariosList();
      });
    }
    getScenarios();





      ///////////////////INIT////////////////////
      pool = new pool();
      refreshScenesList();
      refreshModulesList();
      //refreshscenariosList();


      function refreshScenesList(){ // TO DO à chaque modif ds le dropdown des scenes
        $('#sceneselector').empty();
        $.each(allScenes, function(index,scene){
          $('#sceneselector').append(('<option value="'+index+'">'+scene.name+'</option>'));
        });
      }
      function refreshModulesList(){
        $('#disposms').empty();
        $.each(allModules, function(index,module){
         $('#disposms').append(('<option value="'+index+'">'+module+'</option>'));
        });
        $('#disposms').multipleSelect({width: '100%',selectAll: false, countSelected: false});
        $('#disposms').multipleSelect('refresh');
      }
      function refreshscenariosList(){
        $('#scenariosms').empty();
        $('#scenariosdropdown').empty();
        $.each(allScenarios, function(index,scenario){
          $('#scenariosms').append(('<option value="'+index+'">'+scenario.name+'</option>'));
          $('#scenariosdropdown').append(('<option value="'+index+'">'+scenario.name+'</option>'));
        });

        $('#scenariosms').multipleSelect({width: '100%',selectAll: false, countSelected: false});
        $('#scenariosms').multipleSelect('refresh');
      }



      ////////////// PI COMMANDS //////////////
      $('#addButton').click( function(){
        pool.addPi();
        refreshScenesList();
      });

      $('#delPiButton').click( function(){
        $("#piname").text("Select...");
        $("#disposms").multipleSelect("setSelects", 0);
        $.each(pool.getActivePi(), function(index,pi) {
          pi.deleteLine();
          pool.delPi();
        });

      });

      $('#delBlockButton').click( function(){
        $.each(pool.getActiveBlock(), function(index,block) {
          block.deleteElement();
        });
        $('#blocknameVisu').text("Select...");
        $("#scenariosms").multipleSelect("setSelects", 0);
      });


    ///////////////////INSPECTOR SHOWS////////////////////
    ///////////////////scenarioS
      $('#openscenarioseditor').click( function(){
        $(".inspector").hide();
        $("#scenarioseditor").fadeIn(200);
      });

      $('#closescenarioseditor').click( function(){
        $("#scenarioseditor").hide();
      });

    ///////////////////SCENE
      $('#opensceneeditor').click( function(){
        $(".inspector").hide();
        $("#sceneseditor").hide().fadeIn(100);

      });

      $('#closesceneditor').click( function(){
        $("#sceneseditor").hide();
      });
      /////////////////////////////////////////////////////


      $(".textarea").on("click", function () {
        $(this).select();
      });


      $('.tip').hide();
      var tooltips = false;
      $('#tooltipsOnoff').change(function(){
        tooltips = $('#tooltipsOnoff').prop('checked');
      });


      ///////////////////INSPECTOR SCENE////////////////////
      $('#sceneselector').change(function(){
        var that = $(this);//transforme element dom en objet jquery
        $.each(pool.getActiveBlock(), function(index,block) {
          block.scene = allScenes[that.find(":selected").val()];
          block.refreshInfos();
        });
        $("#scenename").val($('#sceneselector option:selected').text());
      });

      $('#addbtn').click( function(){
        var scenename = $("#scenename").val();
        var newscene = {name:scenename, color:colors[allScenes.length]};
        allScenes.push(newscene);
        refreshScenesList();
        $("#scenename").val("New...");
        //$('#sceneselector').val(allScenes.length-1); // non car sinon confusion est ce que ce groupe a été attribué au bloc ou pas
        });

      $('#modifbtn').click( function(){
        var scenename = $("#scenename").val();
        var indexedited = $('#sceneselector').find(":selected").val();
        allScenes[indexedited].name = scenename;
        refreshScenesList();
        $('#sceneselector').val(indexedited);
      });

      $('#delbtn').click( function(){
        var that = $('#sceneselector');
          var indexedited = that.find(":selected").val();
          allScenes.splice(indexedited,1);
          refreshScenesList();
          $("#scenename").val("New...");
      });

      ///////////////////INSPECTOR DISPO////////////////////
      $('#disposms').change(function() {
        //$("#modulesList").empty();
        var that = $(this);

        $.each(pool.getActivePi(), function(index,pi) {
          var selectedModules = that.multipleSelect("getSelects", "text");
          for (var i = 0, l = selectedModules.length; i < l; ++i) {
           selectedModules[i] = $.trim(selectedModules[i]);
           //$('<li>'+selectedModules[i]+'</li>').appendTo( $('#modulesList') );
           }
           pi.modules = selectedModules;
        });

      });


      ///////////////////INSPECTOR SCENARIOS////////////////////
      $('#scenariosms').change(function() {
        var that = $(this);
        $.each(pool.getActiveBlock(), function(index,block) {
          var selectedScenarios = that.multipleSelect("getSelects", "text");
          for (var i = 0, l = selectedScenarios.length; i < l; ++i) {
           selectedScenarios[i] = $.trim(selectedScenarios[i]);
           }
           block.scenarios = selectedScenarios;
        });
        actuScenarios();
      });

      function actuScenarios(){
        $("#scenariosList").empty();
        var selectedScenarios = $("#scenariosms").multipleSelect("getSelects", "text");
        $.each(selectedScenarios, function(index,scenario) {
          var scenar = scenario.trim();
          $('<li><a target="_blank" href="../_SCENARIO/index.html#'+timelineName+'#'+scenar+'">'+scenario+'</a></li>').addClass('ddd').appendTo( $('#scenariosList') );
        });
      }

      $('#scenariosdropdown').change(function(){
        var that = $(this);
        $("#scenarioname").val($('#scenariosdropdown option:selected').text());
      });


      $('#addscenariobtn').click( function(){
        var scenarioname = $("#scenarioname").val();
        var newscenario = {name:scenarioname};
        allScenarios.push(newscenario);
        refreshscenariosList();
        $("#scenarioname").val("New...");
        recheckscenarios();
      });

      $('#delscenariobtn').click( function(){
        var scenarDelete = $('#scenariosdropdown option:selected').text();
        console.log('DELETING '+scenarDelete);
        $.ajax({
            url: "data/fileDelete.php",
            //dataType: "json",
            type: "POST",
            data: { fileName: scenarDelete, type: 'scenario'}
        });
        $.each(allPi,function(keypi,pi){
          $.each(pi.allBlocks, function(keyblock, block) {
            $.each(block.scenarios, function(key, scenario){
             if (scenario == scenarDelete) { allPi[keypi].allBlocks[keyblock].scenarios.splice(key,1);  }
            });
          });
        });
        getScenarios();
        $("#scenarioname").val("New...");
        recheckscenarios();
      });

      $('#modifscenariobtn').click( function(){
        var oldName = $('#scenariosdropdown option:selected').text();
        var newName = $("#scenarioname").val();
        $.ajax({
            url: "data/fileRename.php",
            type: "POST",
            data: { oldname: oldName, newname: newName, type: 'scenario' }
        }).done(function(reponse){
        });
        $.each(allPi,function(keypi,pi){
          $.each(pi.allBlocks, function(keyblock, block) {
            $.each(block.scenarios, function(key, scenario){
             if (scenario == oldName) { allPi[keypi].allBlocks[keyblock].scenarios[key] = newName ; }
            });
          });
        });
        getScenarios();
        //recheckscenarios();
      });

      function recheckscenarios(){
        // Re-Check les bonnes Cases
        var tempcheck = new Array();
        $.each(pool.getActiveBlock(), function(index,block) {tempcheck = block.scenarios;});
        $("#scenariosms").multipleSelect('setSelects', tempcheck);
      }




     /////////////////////// CLEAR /////////////////////////
      $('#clearBtn').click( function() {
        clearAll();
      });

      function clearAll(){
        $.each(allPi, function(index, pi) {
          pi.line.remove();
          pi.linename.remove();
          $.each(pi.allBlocks, function(index, block) {
            block.keyframe_start.remove();
            block.keyframe_end.remove();
          });
        });
        allPi = [];
        pool.lineCount = 0;
      }


      ///////////////////////// LOAD & SAVE ///////////////////////////////
      /////////////////////////////////////////////////////////////////////
      /////////////////////////////////////////////////////////////////////

      var poolExport = {};
      var timelineName = window.location.hash.substr(1);
      if (timelineName == '') timelineName = 'timeline';
      console.log(timelineName);


      $('#loadBtn').click( function() {
        loadTimeline();
      });


      function loadTimeline() {
          $.ajax({
              url: "data/load.php",
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
                  $('#serverDisplay').html('Loaded: <br>' + reponse.contents );
                  poolExport = JSON.parse(reponse.contents);
                  loadPool();
              }
              else if (reponse.status == 'error')
              { $('#serverDisplay').html( 'Erreur serveur: '+reponse.message ); }
          })
          .fail(function() {
              $('#serverDisplay').html( 'Impossible de joindre le serveur...' );
          });
      }

      $('#saveBtn').click( function() {
        savePool();
          $.ajax({
              url: "data/save.php",
              dataType: "json",
              type: "POST",
              data: {
                  contents: JSON.stringify(poolExport),
                  filename: timelineName,
                  timestamp: $.now(),
                  type: 'timeline'
              }
          })
          .done(function(reponse)
          {
              if (reponse.status == 'success')
              {  $('#serverDisplay').html( 'Saved : <br> '+ JSON.stringify(poolExport) );  }
              else if (reponse.status == 'error')
              { $('#serverDisplay').html( 'Erreur serveur: '+reponse.message ); }
          })
          .fail(function()
            { $('#serverDisplay').html( 'Impossible de joindre le serveur...' ); }
          );

      });




      function savePool(){
        var exportArray = [];

        $.each(allPi, function(indexpi, pi) {
          exportArray.push({
            name: pi.raspiname,
            modules: pi.modules,
            blocks: []
          });
          $.each(pi.allBlocks, function(indexblock, block) {
            exportArray[indexpi].blocks.push({
              name: block.blockName,
              scene: block.scene,
              scenarios: block.scenarios,
              start: block.start.left-108,
              end: block.end.left-108
            })
          });
      });

        poolExport.pool = exportArray;

      }


      function loadPool(){
        clearAll();

        var newPool = poolExport.pool;
        $.each(newPool, function( index, pi ) {
          pool.addPiFromJson(pi.name);
        });

        $.each(allPi, function( indexpi, pi ) {
          pi.recoverPiInfos(newPool[indexpi].modules);

          $.each(newPool[indexpi].blocks, function( indexblk, blk ) {
            pi.allBlocks.push( new block(pi) );
          });

          $.each(pi.allBlocks, function (index, bloc){
            bloc.recoverInfos( newPool[indexpi].blocks[index] );
          });

        });

      }



      //////////////////////// CHOOSE  SCENARIO   /////////////////////////
      /////////////////////////////////////////////////////////////////////
      /////////////////////////////////////////////////////////////////////
  		var allTimelines = [];
  		function loadTimelinesList(){
        allTimelines = [];
        $.ajax({
            url: "data/fileList.php",
  					type: "POST",
            data: { type: 'timeline',
                    directory: './'
            }
        })
        .done(function(filelist) {
          console.log(filelist);
          var alltime = JSON.parse(filelist);
          $.each(alltime,function(index,name){
              var newname = name.replace('.json','');
              allTimelines.push(newname);

          });
          console.log(allTimelines);
  				$.each(allTimelines, function(index,file){
  					$('#selFile').append(('<option value="'+file+'">'+file+'</option>'));
  				});
  				$('#selFile').val(timelineName);
        });
      }
      loadTimelinesList();

  		$('#selFile').change(function(){
  			timelineName = $('#selFile option:selected').text();
        var url = window.location.href.split("#")[0];
  			window.open(url+'#'+timelineName,"_self");
  			location.reload(true);
  		});


});
