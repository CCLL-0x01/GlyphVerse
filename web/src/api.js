const urlPrefix = 'http://127.0.0.1:5000';

export async function generate_character_prompt(char) {
    var response = await fetch(`${urlPrefix}/knowledge_acquisition/${char}`);
    var data = await response.json();
    if (data.code != 0) {
        throw Error(`Resuest Failure: ${data.message}`);
    } else {
        return data.data;
    }
}

export async function upload_img_data(img_data) {
    var formData=new FormData();
    formData.append("file",new Blob([img_data],{type:'image/png'}));
    var response = await fetch(`${urlPrefix}/upload`,{
        method:'POST',
        body:formData,
    });
    var data = await response.json();
    if (data.code != 0) {
        throw Error(`Request Failure: ${data.message}`);
    } else {
        return data.uuid;
    }
}

export async function start_inference(char_data) {
    var response = await fetch(`${urlPrefix}/start`,{
        method:'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(char_data)
    });
    var data = await response.json();
    if (data.code != 0) {
        throw Error(`Request Failure: ${data.message}`);
    } else {
        return data.uuid;
    }
}

export async function query_status(uuid) {
    var response = await fetch(`${urlPrefix}/status/${uuid}`);
    var data = await response.json();
    if (data.code != 0) {
        throw Error(`Request Failure: ${data.message}`);
    } else {
        return data.status
    }
}

export async function start_mask_gen(req_data) {
    var response = await fetch(`${urlPrefix}/mask/start`,{
        method:'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(req_data)
    });

    var data = await response.json();
    if (data.code != 0) {
        throw Error(`Request Failure: ${data.message}`);
    } else {
        return {
            'uuid':data.uuid,
            'job_uuid':data.job_uuid
        }
    }

}

export async function query_mask_status(uuid) {
    var response = await fetch(`${urlPrefix}/mask/status/${uuid}`);
    var data = await response.json();
    if (data.code != 0) {
        throw Error(`Request Failure: ${data.message}`);
    } else {
        return data.status
    }
}