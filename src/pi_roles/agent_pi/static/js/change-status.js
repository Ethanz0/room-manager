function fetchChangeStatus(form) {
    const data = new FormData(form);
    fetch(form.action, {
        method: 'POST',
        body: data,
    })
        .then(message => message.json())
        .then(result => {
            // Optionally handle result, e.g. show a message or update UI
            console.log(result)
            if (result["response"])
                alert(result["response"]);
            if (result["message"])
                alert(result["message"]);
        })
        .then(() => {
            window.location.reload();
        })
        .catch(error => {
            alert('Error updating status');
        });
}