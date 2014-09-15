//
// Strona ankiety => /templates/polls/poll-details.html
// -----------------------------------------------------------------------------

require.config({
    
    baseUrl: window.STATIC_URL,
    
    urlArgs: "bust=" + (new Date()).getTime(),
    
    waitSeconds: 200,
    
    paths: {
        async: 'includes/require/async',
        jquery: 'includes/jquery/jquery',
        bootstrap: 'includes/bootstrap/bootstrap',
        bootbox: 'includes/bootstrap/bootbox',
        underscore: 'includes/underscore/underscore',
        backbone: 'includes/backbone/backbone',
        tagsinput: 'includes/jquery/jquery.tagsinput',
        moment: 'includes/momentjs/moment'
    },
    
    shim: {
        underscore: {
            deps: ['jquery'],
            exports: '_'
        },
        
        backbone: {
            deps: ['underscore'],
            exports: 'Backbone'
        },
        
        bootstrap: {
            deps: ['jquery']
        },
        
        bootbox: {
            deps: ['bootstrap'],
            exports: 'bootbox'
        },
        
        tagsinput: {
            deps: ['jquery']
        }
    }
});

require(['jquery',
         'js/maps/minimap',
         'js/common',
         'js/maps/pointer',
         'js/locations/follow',
         'js/inviter/userinviter'],

function ($, Minimap) {
    
    "use strict";
    
    // Minimapa z markerami (jeżeli są jakieś)
    $(document).ready(function () {
        var minimap = new Minimap(window.MARKERS);
        $('.minimap-toggle-button').on('click', function (e) {
            e.preventDefault();
            minimap.open();
        });
    });
    
    $(document).trigger('load');
    
});