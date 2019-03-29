webiopi().ready(function() {
        		webiopi().setFunction(21,"out");
        		webiopi().setFunction(20,"out");
        		webiopi().setFunction(16,"out");
        		webiopi().setFunction(26,"out");
        		webiopi().setFunction(19,"out");
        		
        		var content, button;
        		content = $("#content");
        		
        		button = webiopi().createGPIOButton(21,"QUARTO");
        		content.append(button);
        		
        		button = webiopi().createGPIOButton(20,"SALA");
        		content.append(button);
        		
        		button = webiopi().createGPIOButton(16,"BANHEIRO");
        		content.append(button);
        		
        		button = webiopi().createGPIOButton(26,"COZINHA");
                content.append(button);
                
                button = webiopi().createGPIOButton(19,"JARDIM");
                content.append(button);
				
				webiopi().refreshGPIO(true);
        		
        });
