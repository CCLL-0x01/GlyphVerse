export async function generate_character_prompt(char){
    var response = await fetch(`/generate_character_prompt/${char}`);
    var data=await response.json();
    if(data.code!=0){
        console.error('Resuest Failure',data.message);
        return;
    }else{
        return data.data;
    }
}