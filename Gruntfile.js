module.exports = function(grunt) {

  // Project configuration.
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    concat: {
      options: {
        banner: '/*! grunt-contrib-concat for <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> */\n'
      },
      css: {
        files: {
          'static/all.css': [
            'bower_components/bootstrap/docs/assets/css/bootstrap.css',
            'bower_components/jquery-ui/themes/base/core.css',
            'bower_components/jquery-ui/themes/base/autocomplete.css',
            'bower_components/jquery.tablesorter/dist/css/theme.blue.css',
            'grunt_files/base.css'
          ]
        }
      },
      jsdevel: {
        files: {
          'static/all.min.js': [
            'bower_components/jquery/dist/jquery.js',
            'bower_components/jquery-ui/jquery-ui.js',
            'bower_components/jquery-ui/ui/widgets/autocomplete.js',
            'bower_components/bootstrap/docs/assets/js/bootstrap.js',
            'bower_components/jquery.tablesorter/dist/js/jquery.tablesorter.combined.js',
            'bower_components/raphael/raphael.min.js',
            'grunt_files/jquery.base.js',
            'grunt_files/jquery.autogrowinput.js',
            'grunt_files/raphael.pie.js'
          ]
        }
      }
    },
    uglify: {
      options: {
        banner: '/*! grunt-contrib-uglify for <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> */\n',
        mangle: { 
            except: [
                'jQuery', 
                'Raphael',
                'kilobytesToSize', 
                'ajax_button_span_url', 
                'show_warning', 
                'log_on_click'] }
      },
      js: {
        files: {
          'static/all.min.js': [
            'bower_components/jquery/dist/jquery.js',
            'bower_components/jquery-ui/jquery-ui.js',
            'bower_components/jquery-ui/ui/widgets/autocomplete.js',
            'bower_components/bootstrap/docs/assets/js/bootstrap.js',
            'bower_components/jquery.tablesorter/dist/js/jquery.tablesorter.combined.js',
            'bower_components/raphael/raphael.min.js',
            'grunt_files/jquery.base.js',
            'grunt_files/jquery.autogrowinput.js',

            // 'grunt_files/jquery.tablesorter.min.js',
            'grunt_files/raphael.pie.js'
          ]
        }
      }
    },
    jshint: {
        all: ['Gruntfile.js', 'grunt_files/*.js']
    }
  });

  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-jshint');

  // Default task(s).
  grunt.registerTask('default', ['concat', 'uglify']);

  // Devel env : just concat files
  grunt.registerTask('devel', ['concat:css', 'concat:jsdevel']);

  grunt.registerTask('test', ['jshint']);
};
