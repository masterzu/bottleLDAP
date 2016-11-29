casper.test.begin('bottleLDAP Accueil', 9, function(test) {
    casper.start("http://localhost:8080", function() {
        test.assertTitle("bottleLDAP |");
	test.assertExists('div#nav');
	test.assertExists('div#nav a');
	test.assertExists('div#nav input#input_search');
	test.assertExists('div#content');
	test.assertExists('div#content div#warning');
	test.assertExists('div#content div#content-text');
	test.assertExists('div#bottom');
        // test.assertExists('form[action="/search"]', "main form is found");
        // this.fill('form[action="/search"]', {
        //     q: "casperjs"
        // }, true);
    });

    casper.thenClick('div#nav a', function(){
        test.assertTitle("bottleLDAP | Tableau de Bord", 'click to homepage');
    });

    casper.run(function() { test.done() });

});

casper.test.begin('bottleLDAP Tableau de bord', 6, function(test) {
    casper.start('http://localhost:8080/servers', function(){
        test.assertTitle("bottleLDAP | Tableau de Bord")
	test.assertExists('#content-text a.ldap')
	test.assertExists('#content-text a.nfs')
    })

    casper.thenClick('#content-text a.ldap', function(){
        test.assertTitle("bottleLDAP | serveur LDAP : myldap", 'click to serveur LDAP')
    })

    casper.then(function(){
	this.back()
    })

    casper.then(function(){
        test.assertTitle("bottleLDAP | Tableau de Bord", 'back to Tableau de Bord')
    })

    casper.thenClick('#content-text a.nfs', function(){
        test.assertTitle("bottleLDAP | serveur NFS : mynfs", 'click to serveur NFS')
    })

    casper.run(function() { test.done() })
});

casper.test.begin('bottleLDAP Master LDAP', 4, function(test) {
    casper.start('http://localhost:8080/server_ldap/myldap', function(){
        test.assertTitle("bottleLDAP | serveur LDAP : myldap")
	test.assertExists('a#issue')
    })

    casper.thenClick('a#issue', function(){
	test.assertExists('#warning')
        // this.echo('wait 1s ...', 'INFO')
    })


    casper.wait(1000, function(){
        test.assertVisible('#warning')
    })

    casper.run(function() { test.done() })
});


// casper.test.begin('bottleLDAP permanents', function(test) {
//     casper.start('http://localhost:8080/users/p', function(){
//         test.assertTitle("bottleLDAP | Utilisateurs")
//     })

//     casper.run(function() { test.done() })
// });

// casper.test.begin('bottleLDAP thesards', function(test) {
//     casper.start('http://localhost:8080/users/d', function(){
//         test.assertTitle("bottleLDAP | Utilisateurs")
//     })

//     casper.run(function() { test.done() })
// });

// casper.test.begin('bottleLDAP etudiants', function(test) {
//     casper.start('http://localhost:8080/users/t', function(){
//         test.assertTitle("bottleLDAP | Utilisateurs")
//     })

//     casper.run(function() { test.done() })
// });

