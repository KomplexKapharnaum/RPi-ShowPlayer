
  $(function() {

    var init = false;

   /////////////////////////////////////////////////////////////////////
   /////////////////////////////////////////////////////////////////////

   //////////////////////// GET NAME TIMELINE .///////////////////////

      function add_button(signal, where) {
          var line = $('<div class="line">');
          var signalName = signal;
           if(signalName == "CARTE_PUSH_1"){
               signalName = "PUSH COURT";
           }else if(signalName == "CARTE_PUSH_11"){
               signalName = "PUSH LONG";
           }else if(signalName == "TELECO_PUSH_OK"){
               signalName = " OK ";
           }else if(signalName == "TELECO_PUSH_A"){
               signalName = " A ";
           }else if(signalName == "TELECO_PUSH_B"){
               signalName = " B ";
           }
          line.append(signalName);
         line.data('id', signal);
         line.on("click", function(e) {
           var idSignal = $(this).data('id');
           console.log('clicked '+idSignal);
             $(this).addClass('lineactive');
           $.ajax({
               url: "/sendSignal",
               type: "POST",
               data: { signal: idSignal }
           }).done(function(r) {
             $(".lineactive").removeClass('lineactive');
               update_info();
           });
         });
         return line;
      }

      function update_info(){
       $.ajax({
         url: "/info",
         dataType: "json"
     }).done(function(r) {
           $("#info").empty();
           $("#info").append(r.device.name+" - "+r.timeline.scenes[r.timeline.activescene]);
           if ( len(r.device.state.teleco.scenario[1]) > 1 &&  r.device.state.teleco.scenario[1] != r.timeline.scenes[r.timeline.activescene])
           //if (teleco in r.device.state) {
               $("#info").append(" - " + r.device.state.teleco.scenario[1]);
           //}
       });
      }
   function draw() {


     $("#teleco").empty();
     $("#carte").empty();

       $("#teleco").append(add_button("TELECO_PUSH_OK"));
       $("#teleco").append(add_button("TELECO_PUSH_A"));
       $("#teleco").append(add_button("TELECO_PUSH_B"));

       $("#carte").append(add_button("CARTE_PUSH_1"));
       $("#carte").append(add_button("CARTE_PUSH_11"));


   }
      setInterval(update_info,2000);
      draw();


});
