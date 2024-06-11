function submitWithAddBtn() {
    document.getElementById('submit').addEventListener('click', function() {
        console.log('submit clicked');
        document.getElementById('add_box').click();
    });
}