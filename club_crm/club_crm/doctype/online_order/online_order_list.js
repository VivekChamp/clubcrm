frappe.listview_settings['Online Order'] = {
    add_fields: ["client_name", "order_date", "cart_status"],
    get_indicator: function(doc) {
        if (doc.cart_status === "Cart") {
            // Draft
            return [__("Cart"), "orange", "cart_status,=,Cart"];
        } else if (doc.cart_status === "Ordered") {
            // Scheduled
            return [__("Ordered"), "green", "cart_status,=,Ordered"];
        } else if (doc.cart_status === "Check-out") {
            // Scheduled
            return [__("Check-out"), "yellow", "cart_status,=,Check-out"];
        } else if (doc.cart_status === "Delivered") {
            // Open
            return [__("Delivered"), "blue", "cart_status,=,Delivered"];
        } else if (doc.cart_status === "Cancelled") {
            // Open
            return [__("Cancelled"), "red", "cart_status,=,Cancelled"];
        }
    }
};