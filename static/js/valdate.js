            $(document).on('click', 'a[href^="#Login"]', function (event) {
                event.preventDefault();

                $('html, body').animate({
                    scrollTop: $($.attr(this, 'href')).offset().top
                }, 700);
            });
//log in comment validate done
$("#val_comment").validate({
            rules:{
                    E_mail: {
                            required: true,
                            email: true
                        },
                    comm:{
                         required: true,
                         minlength: 10
                    }
            }
        }
        );
//log in sign in  validate
$("#val_sign_in").validate({
            rules:{
                    username: {
                            required: true,
                            minlength: 3
                        },
                    password:{
                         required: true,
                         minlength: 5,
                         maxlength: 28
                    }
            }
        }
        );
//log in sign up  validate
$("#val_sign_up").validate({
            rules:{
                    name: {
                            required: true,
                            minlength: 3
                        },
                    id:{
                         required: true,
                         number: true,
                         minlength: 8,
                         maxlength: 8
                    },
                    username:{
                        required: true,
                        minlength: 3
                    },
                    college:{
                        required: true
                    },
                    email:{
                        required: true,
                        email: true
                    },
                    password:{
                       required: true,
                        minlength: 5
                    },
                    confirmpassword:{
                        required: true,
                        // equalTo: "#password"
                    }
                    
            }
        }
        );
// user account validation page done
$("#val_sign_up_new").validate({
            rules:{
                    username: {
                            required: true,
                            minlength: 3
                        },
                    id:{
                         required: true,
                         number: true,
                         minlength: 8,
                         maxlength: 8
                    },
                    college:{
                        equired: true
                    },
                    E_mail:{
                        required: true,
                        email: true
                    },
                    password:{
                       required: true,
                        minlength: 5
                    },
                    confirm_password:{
                        required: true,
                        equalTo: "#password"
                    }
                    
            }
        }
        );
// college page validation 
$("#add_resarch").validate({
            rules:{
                    name:{
                        required: true,
                            minlength: 3
                    },
                    aothor:{
                        required: true,
                        minlength: 3
                    },
                    date:{
                        required: true 
                    },
                    college:{
                       required: true  
                    },
                    file:{
                        required: true
                    }
                    
            }
        }
        );
$("#edit_resarch").validate({
            rules:{
                    resaerch_name:{
                        required: true,
                            minlength: 3
                    },
                    author_name:{
                        required: true,
                        minlength: 3
                    },
                    publish:{
                        required: true 
                    },
                    college:{
                       required: true  
                    },
                    file:{
                        required: true
                    }
                    
            }
        }
        );
//College page validation
$("#add_college").validate({
            rules:{
                    name: {
                            required: true,
                            lettersonly: true,
                            minlength: 3
                        }

            }
        }
        );
$(document).on('click', 'a[href^="#Login"]', function (event) {
                event.preventDefault();

                $('html, body').animate({
                    scrollTop: $($.attr(this, 'href')).offset().top
                }, 700);
});
