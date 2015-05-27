
  $(function() {


		var urlbase = '';
		//var urlbase = 'http://192.168.0.19:8080';

    $('#colonne2').hide();
    setTimeout(function(){
      loadTimeline();
      $('#colonne2').fadeIn(200);
    },200);


    function pool() {

      allPi = new Array();
      this.lineCount = 0;


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
        pool.lineCount++;
        allPi.push(new pi("Pi"+pool.lineCount));
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
        $.each(allPi,function(index,pi){
          $.each(pi.allBlocks,function(index,block){
            $.each(allScenes,function(index,scene){
              if (block.scene == scene.name){
            		block.blockbox.css({
            		  'left': scene.start-gridleft
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
      ///AVOID DOUBLONS
			$.each(allScenes,function(index,scene){
				var count = scene.name.replace('SC','');
				if (count == sceneCount) { sceneCount++; }
			});

      allScenes.push(new scene());
      pool.getScenes();

    });


    $('#allscenes').sortable({
      axis: "x",
      cursor: "move",
      tolerance: "pointer",
      start: function (event, ui) {
          pool.getScenes();
      },
      sort: function(){
        $.each(allScenes,function(index,scene){ scene.actuPosition();})
        pool.followScenes();
      },
      stop: function (event, ui) {
        $.each(allScenes,function(index,scene){ scene.actuPosition();})
        pool.followScenes();

        $.each(allPi,function(index,pi){
          $.each(pi.allBlocks,function(index,block){
            block.actuPosition();
          });
        });

        allScenes.sort(function(sc1, sc2) {
        	return sc1.start - sc2.start;
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
        thisScene.editInfos();
      });

      this.editInfos = function(){
        $.each(allScenes,function(index,scene){
          scene.scenebox.css('background-color','#444444');
          scene.active = false;
        })
        thisScene.scenebox.css('background-color','#BABABA');
        $('#scenename').text(thisScene.name);
        thisScene.active = true;
      }

      this.recoverInfos = function(name, position){
        thisScene.name = name;
        thisScene.scenebox.text(name);
        //thisScene.scenebox.css({left:position});
        //BUG SORTABLE SI CA ??? :
        // var scenepos = thisScene.scenebox.offset();
        // scenepos.left = position+gridleft;
        // this.scenebox.offset(scenepos);
        // thisScene.actuPosition();
      }

      this.getBlocks = function(){
        var sceneBlocks = new Array();
          $.each(allPi,function(index,pi){
            $.each(pi.allBlocks,function(index,block){
              if (block.start == thisScene.start){ sceneBlocks.push(block); }
              //if (block.scene == thisScene.name){ sceneBlocks.push(block); }
            });
          });
        return sceneBlocks;
        }


    }
    ////////////////////// SCENE DELETE /////////////////////////
    /////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////

    $('#delSceneButton').click(function(){
      var indextoremove;
      pool.getScenes();

      $.each(allScenes, function(key, scene) {
        if (scene.active) {
          scene.scenebox.remove();
          indextoremove = key;
          $.each(scene.getBlocks(),function(index,block){
            console.log(block.blockName);
            block.deleteElement();
          });
        }
      });
      allScenes.splice(indextoremove,1);

      $.each(allScenes, function(key, scene) {
        scene.actuPosition();
      });
      pool.followScenes();

      $.each(allPi,function(index,pi){
        $.each(pi.allBlocks,function(index,block){
            block.actuPosition();
        });
      });
      pool.getScenes();

    });
    //////////////////////  SCENE NAME  /////////////////////////
    /////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////
    $('#scenename').click(function(e){

      var sceneName = $('<input>').attr('type', 'text').addClass("textareaSmall");

      var editedScene;
      $.each(allScenes, function(key, scene) {
        if (scene.active) { editedScene = scene; }
      });

      $(this).text("");
      $('#scenename').append(sceneName);
      sceneName.val(editedScene.name);
      sceneName.focus();
      listenToEnter();
      e.stopPropagation();


      function listenToEnter(){
      sceneName.focusout(function() {
  			$(this).parent().text(this.value);
        editedScene.name = this.value;
        editedScene.scenebox.text(this.value);
        $("#scenename").text(editedScene.name);
  		});
      }
      listenToEnter();
  		sceneName.focus();

      pool.getScenes();


    });





    ////////////////////////// PI SORT //////////////////////////
    /////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////


    var gridheight;
    var gridwidth;
    var gridtop = $('#allpi').offset().top;
    var gridleft =  $('#allpi').offset().left;

    var sorting = false;

    $('#allpinames').sortable({
      axis: "y",
      start: function(){ sorting = true; $('.tip').hide(); },
      sort: function(){
        $.each(allPi,function(index,pi){
          var linenamePos = pi.linename.offset().top-(gridheight*index)-gridtop;
          pi.line.css({top:linenamePos});
        });

      },
      stop: function (event, ui) {
        //console.log(ui.item.offset().top);
        $.each(allPi,function(index,pi){
          var linenamePos = pi.linename.offset().top-(gridheight*index)-gridtop;
          pi.line.css({top:linenamePos});
          pi.lineheight = pi.linename.offset().top;
          //console.log(index + ' '+pi.lineheight);
        });

        // si on trie maintenant ca fout le bordel ??
        // allPi.sort(function(pi1, pi2) {
        // 	return pi1.lineheight - pi2.lineheight;
        // });
        //
        // $.each(allPi,function(index,pi){
        //   console.log(index + ' '+pi.lineheight + ' '+ pi.raspiname);
        // });
        sorting = false;

      }
    });


    ////////////////////////// PI OBJECT ////////////////////////
    /////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////
    function pi(id) {

      this.allBlocks = new Array();
      this.blockCount = 0;
      this.linename = $('<div>').addClass('linename').appendTo( $('#allpinames') );
      this.linename.hide().fadeIn(150);
      this.line = $('<div>').addClass('line').appendTo( $('#allpi') );
      this.line.hide().fadeIn(150);
      this.line.attr('id', id);
      this.raspiname = id;
      this.linename.text(this.raspiname);
      this.modules = new Array();
      pool.unselectLines();
      this.active = false;
      var thispi = this;
      this.lineheight = this.linename.offset().top;
      this.infos = '...';


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
        $('#disposelector').val(thispi.raspiname);
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

      this.recoverPiModules = function(mod){
        thispi.modules = mod;
      }

      this.recoverPiInfos = function(){
        $.each(disposList,function(index,dispo){
          if (dispo.hostname == thispi.raspiname){
            thispi.infos = dispo.infos;
          }
        });
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
      }

      ///////////////////SCENE TIPS///////////////////////
      this.linename.mouseenter(function(e){
        $('.tip').html('');
        $('.tip').append(thispi.infos+'<br>');
      });
      this.linename.mousemove(function(e){
        if ( (tooltips == true)&&(sorting == false)){ $('.tip').show();}
        $('.tip').css({ 'top': e.pageY-14,'left': e.pageX+18 });
      });
      this.linename.mouseout(function(){
        $('.tip').hide();
      });

    }


    /////////////////////// BLOCK OBJECT ////////////////////////
    /////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////
    function block(thispi) {

      thispi.blockCount++;
      var thisblock = this;
      this.blockbox = $('<div>').addClass('block');
      thispi.line.append(this.blockbox);
      gridheight = this.blockbox.height();
      gridwidth = this.blockbox.width();
      this.blockName = "block" +thispi.blockCount;
      this.blockbox.attr('id', this.blockName);
      //this.group = allgroups[0];
      this.group = 'default';
      this.scene = 'scene_lambda';
      this.scenarios = [];
      pool.unselectBlocks();
      this.active = false;


      this.blockbox.on('click', function () {
        pool.unselectBlocks();
        thisblock.active = true;
        thisblock.editInfos();
        $(this).css('opacity', '.9');
      });

      this.editInfos = function(){
        $('#blocknameVisu').text(thisblock.blockbox.attr('id'));
        var groupname = thisblock.group;
        $('#groupselector').val(
          $('#groupselector option').filter(function(){ return $(this).html() == groupname; }).val()
        );

        $('#scenarioname').val(thisblock.scene+'_temp');
        ///////////// SORTING SCENARIOS
        $("#scenariosms").empty();
        $('#scenariosdropdown').empty();
        //Creating array of scenes names
        var scenesList = new Array();
        $.each (allScenes, function(index,scene){ scenesList.push(scene.name) });
        //sort
        $.each(allScenarios,function(index,scenario){
          var sceno = scenario.name.split('_')[0];
          //console.log(sceno);
          if (sceno == thisblock.scene){
            //console.log(sceno);
            $('#scenariosms').append(('<option value="'+index+'">'+scenario.name+'</option>'));
            $('#scenariosdropdown').append(('<option value="'+index+'">'+scenario.name+'</option>'));
          }
          if(($.inArray(sceno, scenesList)==-1)&&(scenario.name.indexOf('_')==-1)) {
            //console.log(sceno);
            $('#scenariosms').append(('<option value="'+index+'">'+scenario.name+'</option>'));
            $('#scenariosdropdown').append(('<option value="'+index+'">'+scenario.name+'</option>'));
          }
        });
        $('#scenariosms').multipleSelect('refresh');
        ///////////////RECHECK SCENARIOS
        var toCheck = new Array();
        $.each(this.scenarios, function(index,scenario){
          $.each(allScenarios, function(key,scenar){
            if (scenario === scenar.name) { toCheck.push(key);}
          });
        });
        $("#scenariosms").multipleSelect("setSelects", toCheck);
        thisblock.getScene();

      }

      this.refreshInfos = function(){
        var thecolor;
        $.each(allgroups, function(index,group){
          if (group.name == thisblock.group){ thecolor = group.color; }
        });
        thisblock.blockbox.css('backgroundColor', thecolor);
      }


      this.deleteElement = function(){
        var indextoremove;
        $.each(thispi.allBlocks, function(index, block) {
          if (block.active) indextoremove = index;
        });
        thispi.allBlocks.splice(indextoremove,1);
        thisblock.blockbox.remove();

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
        // console.log(thisblock.scene);
        // console.log(thisblock.start);
      }
      this.getScene();

      //////////////////DRAGGABLE////////////////////////
      thisblock.blockbox.draggable({
        grid: [ 50,50 ],
        axis: "x",
        distance: 50,
        containment: "parent",
        drag: function(){
          thisblock.actuPosition();
        },
        stop: function(){
          thisblock.scenarios = [];
          thisblock.group = 'default';
          thisblock.getScene();
          thisblock.refreshInfos();
        }
        });

      ///////////////////TOOLTIPS///////////////////////
      this.blockbox.mouseenter(function(e){
        $('.tip').html('');
        $('.tip').append('Scene: '+thisblock.scene+'<br>'+'Groupe: '+thisblock.group+'<br>'+'Scenarios: '+'<br>');
        $.each(thisblock.scenarios,function(index,scenar){
          $('.tip').append(scenar+'<br>');
        });
      });
      this.blockbox.mousemove(function(e){
        if (tooltips == true){ $('.tip').show();}
        $('.tip').css({ 'top': e.pageY-14,'left': e.pageX+18 });
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
  		  //url: "http://2.0.1.89:8080/moduleslist",
        url: urlbase+"/moduleslist",
  			dataType: "jsonp",
  		}).done(function(data) {
        allModules = {};
  			allModules = data;
        refreshModulesList();
  		});


  //////////////////// groupS ///////////////////EF7126
    var colors = new Array ('B5B5B5','218C8D','D83E3E','F9E559','3F7CAC','8EDC9D','A05C7B','E1CE9A','75C1FF','82A647', 'EF7126','9B6236','C4E00F','F4FF52','6E0014');
    var group0 = {name:'default', color:colors[0]};
    var group1 = {name:'group1', color:colors[1]};
    var group2 = {name:'group2', color:colors[2]};
    var group3 = {name:'group3', color:colors[3]};
    var group4 = {name:'group4', color:colors[4]};
    var group5 = {name:'group5', color:colors[5]};
    var group6 = {name:'group6', color:colors[6]};
    var group7 = {name:'group7', color:colors[7]};
    var group8 = {name:'group8', color:colors[8]};
    var group9 = {name:'group9', color:colors[9]};
    var group10 = {name:'group10', color:colors[10]};
    var allgroups = new Array();
    allgroups.push(group0);
    allgroups.push(group1);
    allgroups.push(group2);
    allgroups.push(group3);
    allgroups.push(group4);
    allgroups.push(group5);
    allgroups.push(group6);
    allgroups.push(group7);
    allgroups.push(group8);
    allgroups.push(group9);
    allgroups.push(group10);

    //////////////////// SCENARIOS ///////////////////
    var allScenarios = new Array();

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
        var scenariosList = filelist;
        if( Object.prototype.toString.call( scenariosList ) !== '[object Array]' ) {
          scenariosList = JSON.parse(scenariosList);
        }
        $.each(scenariosList,function(index,name){
          if (name !== 'library.json'){
            var newname = name.replace('.json','');
            var scenar = {name:newname,active:false};
            allScenarios.push(scenar);
          }
        });
        refreshscenariosList();
        actuScenarios();
        recheckScenarios();
      });
    }
    getScenarios();



    ///////////////////INIT////////////////////
    pool = new pool();
    refreshgroupsList();
    refreshModulesList();


    function refreshgroupsList(){ // TO DO à chaque modif ds le dropdown des groups
      $('#groupselector').empty();
      $.each(allgroups, function(index,group){
        $('#groupselector').append(('<option value="'+index+'">'+group.name+'</option>'));
      });
    }
    $("#groupselector option:odd").css("background-color","red");

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
  ///////////////////Scenarios
    $('#openscenarioseditor').click( function(){
      $(".inspector").hide();
      $("#scenarioseditor").fadeIn(200);
    });

    $('#closescenarioseditor').click( function(){
      $("#scenarioseditor").hide();
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


    ///////////////////GROUP SELECTOR////////////////////
    $('#groupselector').change(function(){
      var that = $(this);
      $.each(pool.getActiveBlock(), function(index,block) {
        block.group = $('#groupselector option:selected').text();
        block.refreshInfos();
      });
    });


    ///////////////////INSPECTOR DISPO////////////////////
    $('#disposms').change(function() {
      var that = $(this);
      $.each(pool.getActivePi(), function(index,pi) {
        var selectedModules = that.multipleSelect("getSelects", "text");
        for (var i = 0, l = selectedModules.length; i < l; ++i) {
          selectedModules[i] = $.trim(selectedModules[i]);
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
      recheckScenarios();
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
    });

    function recheckScenarios(){
      // Re-Check les bonnes Cases
      $.each(pool.getActiveBlock(), function(index,block) {block.editInfos();});
      // var tempcheck = new Array();
      // $.each(pool.getActiveBlock(), function(index,block) {tempcheck = block.scenarios;});
      // console.log(tempcheck);
      // $("#scenariosms").multipleSelect('setSelects', tempcheck);
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
      $.each(allScenes,function(index,scene){
        scene.scenebox.remove();
      });
      allScenes = [];
      sceneCount = 0;
      pool.lineCount = 0;
    }


    ///////////////////////// LOAD & SAVE ///////////////////////////////
    /////////////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////

    var exportArray = {};
    var timelineName = window.location.hash.substr(1);
    if (timelineName == '') timelineName = 'timeline';
    console.log(timelineName);


    $('#loadBtn').click( function() {
      loadTimeline();
      $('#scenename, #piname, #blocknameVisu').text("Select...");
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
                exportArray = JSON.parse(reponse.contents);
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
                contents: JSON.stringify(exportArray),
                filename: timelineName,
                timestamp: $.now(),
                type: 'timeline'
            }
        })
        .done(function(reponse)
        {
            if (reponse.status == 'success')
            {
              $('#serverDisplay').html( 'Saved : <br> '+ JSON.stringify(exportArray) );
            }
            else if (reponse.status == 'error')
            { $('#serverDisplay').html( 'Erreur serveur: '+reponse.message ); }
        })
        .fail(function()
          { $('#serverDisplay').html( 'Impossible de joindre le serveur...' ); }
        );

    });


    function savePool(){
      var exportPool = [];
      //sort Order en fonction de la position --> pour la reconstruction
      // (si on fa ca a chaque sorting, on perd le fil des indexs ??)
      allPi.sort(function(pi1, pi2) {
      	return pi1.lineheight - pi2.lineheight;
      });

      $.each(allPi, function(indexpi, pi) {
        exportPool.push({
          name: pi.raspiname,
          modules: pi.modules,
        //infos: pi.infos,
          blocks: []
        });
        $.each(pi.allBlocks, function(indexblock, block) {
          exportPool[indexpi].blocks.push({
            name: block.blockName,
            group: block.group,
            scenarios: block.scenarios,
            start: block.start-gridleft,
            end: block.end-gridleft,
            keyframe: (block.start-gridleft)/gridwidth
          })
        });
      });

      var exportScenes = [];
      $.each(allScenes, function(index,scene){
        exportScenes.push({
          name: scene.name,
          position: scene.start-gridleft,
          keyframe: (scene.start-gridleft)/gridwidth
        })

      });

      exportArray.pool = exportPool;
      exportArray.scenes = exportScenes;

    }


    function loadPool(){
      clearAll();

      var newPool = exportArray.pool;
      $.each(newPool, function( index, pi ) {
        pool.addPiFromJson(pi.name);
      });

      $.each(allPi, function( indexpi, pi ) {
        pi.recoverPiModules(newPool[indexpi].modules );

        $.each(newPool[indexpi].blocks, function( indexblk, blk ) {
          pi.allBlocks.push( new block(pi) );
        });

        $.each(pi.allBlocks, function (index, bloc){
          bloc.recoverInfos( newPool[indexpi].blocks[index] );
        });

      });

      var newScenes = exportArray.scenes;
      $.each(newScenes, function(key,newscene){
        allScenes.push(new scene());
      });
      $.each(allScenes,function(keyscene,scene){
        scene.recoverInfos(newScenes[keyscene].name, newScenes[keyscene].position);
      })

      pool.getScenes();
      getDisposList();

    }


    //////////////////////// CHOOSE  TIMELINE   /////////////////////////
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
        var alltime = filelist;
        if( Object.prototype.toString.call( alltime ) !== '[object Array]' ) {
          alltime = JSON.parse(alltime);
        }
        $.each(alltime,function(index,name){
            var newname = name.replace('.json','');
            allTimelines.push(newname);

        });
        //console.log(allTimelines);
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

    //////////////////////// CHOOSE  DISPO   ////////////////////////////
    /////////////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////
    var dispotemp = {hostname:'Select...', infos: 'when', active: 'yes'};
    var dispo1 = {hostname:'dispo1', infos: 'when', active: 'yes'};
    var dispo2 = {hostname:'dispo2', infos: 'where', active: 'yes'};
    var dispo3 = {hostname:'dispo3', infos: 'what', active: 'yes'};
    var dispo4 = {hostname:'dispo4', infos: 'who', active: 'yes'};

    var disposList = new Array();
    disposList.push(dispotemp);
    disposList.push(dispo1);
    disposList.push(dispo2);
    disposList.push(dispo3);
    disposList.push(dispo4);

    // DO after loadTimeline(), --> recoverPiInfos finds raspiname
    function getDisposList(){
  		$.ajax({
  			type: 'GET',
  			timeout: 1000,
  		  //url: "http://2.0.1.89:8080/disposList",
        url: urlbase+'/disposList',
  			dataType: "jsonp",
  		}).done(function(data) {
  			disposList = data.devices;
  			disposList.unshift(dispotemp);
        updateDispos();
        $.each(allPi, function( indexpi, pi ) {
          pi.recoverPiInfos();
        });
  		});
    }

		function updateDispos(){
			$('#disposelector').empty();
			$.each(disposList, function(index,dispo){
        if (dispo.active == 'yes'){
	        $('#disposelector').append(('<option value="'+dispo.hostname+'">'+dispo.hostname+'</option>'));
        }
			});
		}
		updateDispos();

    $('#disposelector').change(function(){
      var editedPi;
      $.each(pool.getActivePi(), function(index,pi) {
        editedPi = pi;
      });
      var newval = $('#disposelector option:selected').text();
      if (editedPi != null){
        editedPi.raspiname = newval
        editedPi.linename.text(newval);
        $('#piname').text(newval);
        $.each(disposList,function(index,dispo){
          if (dispo.hostname == newval){
            editedPi.infos = dispo.infos;
          }
        });

      }
    });



});
