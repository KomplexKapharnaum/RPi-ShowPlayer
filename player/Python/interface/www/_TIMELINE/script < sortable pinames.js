
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

      this.getScenes = function(){
        $.each(allPi,function(index,pi){
          $.each(pi.allBlocks,function(index,block){
            $.each(allScenes,function(index,scene){
              if (block.start == scene.start){
                block.scene = scene.name;
                }
            });
          });
        });
      }
      this.followScenes = function(){
        console.log("YO");
        $.each(allPi,function(index,pi){
          $.each(pi.allBlocks,function(index,block){
            $.each(allScenes,function(index,scene){
              if (block.scene == scene.name){
            		block.blockbox.css({
            		  'left': scene.start-108
            		});
              }
            });
          });
        });

      }


    }
    /////////////////////// SCENE OBJECT ////////////////////////
    /////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////

    var sceneCount = 0;
    var allScenes = new Array();
    $('#allscenes').dblclick(function(){
      sceneCount++;
      allScenes.push(new scene());
      console.log(allScenes);
      pool.getScenes();
    });


    $('#allscenes').sortable({
      axis: "x",
      cursor: "move",
      tolerance: "pointer",
      start: function (event, ui) {
          //console.log($(ui.item).data("startindex", ui.item.index()));
          pool.getScenes();
      },
      sort: function(){
        $.each(allScenes,function(index,scene){ scene.actuPosition();})
        pool.followScenes();
      },
      stop: function (event, ui) {
        //console.log(ui.item.offset().left);
        $.each(allScenes,function(index,scene){ scene.actuPosition();})
        pool.followScenes();

        $.each(allPi,function(index,pi){
          $.each(pi.allBlocks,function(index,block){
            block.actuPosition();
          });
        });

      }

    });

    function scene(){

      this.scenebox = $('<div>').addClass('scene').appendTo( $('#allscenes') );

      this.active = false;
      var thisScene = this;
      this.name = 'SC'+sceneCount;
      this.scenebox.text(this.name);

      if (this.scenebox.prev().hasClass("scene")) {
       var prev = this.scenebox.prev();
       var scenepos = this.scenebox.offset();
       var prevpos = prev.offset();
       var prevwidth = prev.width();
       scenepos.left = prevpos.left + prevwidth;
       this.scenebox.offset(scenepos);
      }

      this.actuPosition = function(){
      var w = thisScene.scenebox.width();
      var offset = thisScene.scenebox.offset();
      this.start=offset.left;
      this.end = offset.left + w;
      }
      this.actuPosition();



      this.scenebox.on('click',function(){
        console.log(thisScene.start);
        $.each(allScenes,function(index,scene){
          scene.scenebox.css('background-color','#444444');
        })
        thisScene.scenebox.css('background-color','#BABABA');
      });



    }








    /////////////////////// PI OBJECT ////////////////////////
    //////////////////////////////////////////////////////////
    function pi(id) {


      this.allBlocks = new Array();
      this.blockCount = 0;
      this.linename = $('<div>').addClass('linename').appendTo( $('#allpinames') );
      this.linename.hide().fadeIn(150);
      this.line = $('<div>').addClass('line').appendTo( $('#allpi') );
      this.line.hide().fadeIn(150);

      this.line.attr('id', id);
      //this.line.sortable();

      this.raspiname = id;
      this.linename.text(this.raspiname);
      this.modules = new Array();
      pool.unselectLines();
      this.active = false;

      var thispi = this;

      this.line.dblclick( function()
      {
        thispi.allBlocks.push(new block(thispi));
        $("#blocknameVisu").text("Select...");
        $("#scenariosms").multipleSelect("setSelects", 0);
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

    var dragged;
    $('#allpinames').sortable({
      axis: "y",

      start: function (event, ui) {
          //console.log($(ui.item).data("startindex", ui.item.index()));
          dragged = ui.item.text();
          console.log(dragged);
      },
      sort: function(){
        //console.log(this);
      },
      stop: function (event, ui) {
        console.log(ui.item.offset().top);
        //$('#'+dragged).css({ 'top': ui.item.offset().top});
      }
    });

    $.each(allPi,function(index,pi){
      
    })

    /////////////////////// BLOCK OBJECT ////////////////////////
    /////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////
    function block(thispi) {

      thispi.blockCount++;
      var thisblock = this;
      //var block = $('<div>').addClass('block');
      this.blockbox = $('<div>').addClass('block');

      thispi.line.append(this.blockbox);


      this.blockName = "block" +thispi.blockCount;
      this.blockbox.attr('id', this.blockName);


      this.group = allgroups[0];
      this.scene = 'scene_lambda';

      this.scenarios = [];
      pool.unselectBlocks();
      this.active = true;
      $('#blocknameVisu').text(thisblock.blockbox.attr('id'));


      this.blockbox.on('click', function () {
        pool.unselectBlocks();
        thisblock.active = true;
        thisblock.editInfos();
        $(this).css('opacity', '.9');
      });


      this.editInfos = function(){
        $('#blocknameVisu').text(thisblock.blockbox.attr('id'));
        var groupname = thisblock.group.name;
        $('#groupselector').val(
          $('#groupselector option').filter(function(){ return $(this).html() == groupname; }).val()
        );
        var toCheck = new Array();
        $.each(this.scenarios, function(index,scenario){
          $.each(allScenarios, function(key,scenar){
            if (scenario === scenar.name) { toCheck.push(key);}
          });

        });
        $("#scenariosms").multipleSelect("setSelects", toCheck);
        thisblock.getScene();
        console.log(thisblock.scene);
        }




      this.refreshInfos = function(){
        thisblock.blockbox.css('backgroundColor', thisblock.group.color);
      }


      this.deleteElement = function(){
        var indextoremove;
        $.each(thispi.allBlocks, function(index, block) {
          if (block.active) indextoremove = index;
        });
        thispi.allBlocks.splice(indextoremove,1);
        thisblock.blockbox.remove();

        $.each(thispi.allBlocks, function(index, block) {
        block.keyframePosition();
        });
      }

      this.recoverInfos = function(infos){
        thisblock.name = infos.name;
        thisblock.blockbox.css({left:infos.start});
        thisblock.blockbox.width(infos.end-infos.start);
        thisblock.scenarios = infos.scenarios;
        thisblock.group = infos.group;
        thisblock.refreshInfos();
        thisblock.actuPosition();
      }

      //Move after prev (if prev is a block)
      if (thisblock.blockbox.prev().hasClass("block")) {
        var prev = thisblock.blockbox.prev();
        var blockpos = thisblock.blockbox.offset();
        var prevpos = prev.offset();
        var prevwidth = prev.width();
        blockpos.left = prevpos.left + prevwidth;
        thisblock.blockbox.offset(blockpos);
      }

      this.actuPosition = function(){
      var w = thisblock.blockbox.width();
      var offset = thisblock.blockbox.offset();
      this.start=offset.left;
      this.end = offset.left + w;
      }
      this.actuPosition();


      this.getScene = function(){
        $.each(allScenes,function(index,scene){
          if (thisblock.start == scene.start){
            thisblock.scene = scene.name;
            }
        });
      }
      //this.getScene();

      ////////////////////////////////////////////////////
      var resized = true;
      // block.resizable({
      //   handles: "e",
      //   grid: 50,
      //   containment: "parent",
      //   resize: function() {
      //     thisblock.keyframePosition();
      //     $.each(thispi.allBlocks, function(index, block) {
      //     block.keyframePosition();
      //     });
      //     resized = false;
      //     setTimeout(function(){ resized = true },1000);
      //   }
      // });
      thisblock.blockbox.draggable({
        grid: [ 50,50 ],
        axis: "x",
        containment: "parent",
        drag: function(){
          thisblock.actuPosition();
        }
        });


      ///////////////////TOOLTIPS///////////////////////
      this.blockbox.mouseenter(function(e){
        $('.tip').html('');
        $('.tip').append(thisblock.scene+'<br>');
        // $.each(thisblock.scenarios,function(index,scenar){
        //   $('.tip').append(scenar+'<br>');
        // });
      });
      this.blockbox.mousemove(function(e){
        if (resized == true && tooltips == true){
          $('.tip').show();
        }
        $('.tip').css({ 'top': e.pageY+25,'left': e.pageX-30 });
      });

      this.blockbox.mouseout(function(){
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


  //////////////////// groupS ///////////////////
  var colors = new Array ('B5B5B5','218C8D','D83E3E','F9E559','EF7126','8EDC9D','A05C7B',
  'E1CE9A','3F7CAC','E21D1D','82A647','9B6236','75C1FF','C4E00F','F4FF52','6E0014');
    var group0 = {name:'default', color:colors[0]};
    var group1 = {name:'group1', color:colors[1]};
    var group2 = {name:'group2', color:colors[2]};
    var group3 = {name:'group3', color:colors[3]};
    var group4 = {name:'group4', color:colors[4]};
    var group5 = {name:'group5', color:colors[5]};
    var group6 = {name:'group6', color:colors[6]};
    var group7 = {name:'group7', color:colors[7]};
    var allgroups = new Array();
    allgroups.push(group0);
    allgroups.push(group1);
    allgroups.push(group2);
    allgroups.push(group3);
    allgroups.push(group4);
    allgroups.push(group5);
    allgroups.push(group6);
    allgroups.push(group7);


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
    refreshgroupsList();
    refreshModulesList();
    //refreshscenariosList();


    function refreshgroupsList(){ // TO DO à chaque modif ds le dropdown des groups
      $('#groupselector').empty();
      $.each(allgroups, function(index,group){
        $('#groupselector').append(('<option value="'+index+'">'+group.name+'</option>'));
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
      refreshgroupsList();
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

  ///////////////////group
    $('#opengroupeditor').click( function(){
      $(".inspector").hide();
      $("#groupseditor").hide().fadeIn(100);

    });

    $('#closegroupditor').click( function(){
      $("#groupseditor").hide();
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


    ///////////////////INSPECTOR group////////////////////
    $('#groupselector').change(function(){
      var that = $(this);//transforme element dom en objet jquery
      $.each(pool.getActiveBlock(), function(index,block) {
        block.group = allgroups[that.find(":selected").val()];
        block.refreshInfos();
      });
      $("#groupname").val($('#groupselector option:selected').text());
    });

    $('#addbtn').click( function(){
      var groupname = $("#groupname").val();
      var newgroup = {name:groupname, color:colors[allgroups.length]};
      allgroups.push(newgroup);
      refreshgroupsList();
      $("#groupname").val("New...");
      //$('#groupselector').val(allgroups.length-1); // non car sinon confusion est ce que ce groupe a été attribué au bloc ou pas
      });

    $('#modifbtn').click( function(){
      var groupname = $("#groupname").val();
      var indexedited = $('#groupselector').find(":selected").val();
      allgroups[indexedited].name = groupname;
      refreshgroupsList();
      $('#groupselector').val(indexedited);
    });

    $('#delbtn').click( function(){
      var that = $('#groupselector');
        var indexedited = that.find(":selected").val();
        allgroups.splice(indexedited,1);
        refreshgroupsList();
        $("#groupname").val("New...");
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
            {
              $('#serverDisplay').html( 'Saved : <br> '+ JSON.stringify(poolExport) );
            }
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
            group: block.group,
            scenarios: block.scenarios,
            start: block.start-108,
            end: block.end-108
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
