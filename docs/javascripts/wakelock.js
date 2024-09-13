document$.subscribe(function() {
    const toggle = '<label class="wakelock" for="wakelock-toggle">Keep screen on<label class="switch"> <input id="wakelock-toggle" type="checkbox"> <span class="slider round"></span> </label></label>'
    $("#ingredients").before(toggle)
    let wakelock;
    const canWakeLock = () => 'wakeLock' in navigator;
    $('#wakelock-toggle').on("change", async function(){
        if(!canWakeLock()) return;
        try {
            if (wakelock) {
                wakelock.release();
                wakelock = null;
            } else {
                wakelock = await navigator.wakeLock.request();
            }
        } catch(e) {
            console.error('Failed to lock wake state with reason:', e.message);
        }
    })
})
