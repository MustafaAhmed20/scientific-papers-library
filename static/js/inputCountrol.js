var cont = 1;
var is_plus_show = true;
if(cont == 1)
{
    $("#deleteBtn").fadeOut(1);
}
function add() 
{
    if(cont != 4)
    {
        cont++;
        if(cont == 4)
        {
            $("#addBtn").fadeOut();
            is_plus_show = false;
        }
        var txt1 = "<input type='text' style='margin-top:5px' name='"+cont+"'placeholder='"+cont+ "' class='"+cont+" form-control'  required >";                   
        var html_result = "." + (cont-1);
        $(html_result).after(txt1);
        $("#deleteBtn").fadeIn();
    }
}
function remove()
{
    var html_result = "." + cont;
    
    if(!is_plus_show)
    {
        $("#addBtn").fadeIn();
    }
    
    if(cont != 1)
    {
        $("input").remove(html_result);
        cont--;
    }
    if(cont == 1)
    {
        $("#deleteBtn").fadeOut();
    }
}