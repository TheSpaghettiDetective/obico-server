(function(Mustache) {
    /**
     * CachedTemplate
     *
     * Stores the text of a template
     */
    var CachedTemplate = function(template, partials) {
        var self = this;

        /**
         * CachedTemplate.template
         * 
         * The text of the template.
         */
        self.template = template;
        
        /**
         * CachedTemplate.partials
         * 
         * An object containing the text of partials used in the template.
         */
        self.partials = partials;

        /**
         * CachedTemplate.render(view, partials, send_fun)
         * 
         * Turns this template into HTML using the given view data.
         */
        self.render = function(view, partials, send_fun) {

            // Use either the parials specified, or the entire set of templates
            // stored in Mustache.TEMPLATES
            partials = partials || self.partials || Mustache.TEMPLATES;

            return Mustache.to_html(self.template, view, partials, send_fun);
        };
    };

    /**
     * Mustache.template(name)
     * 
     * Creates and returns a new CachedTemplate object containing the template
     * referred to by the given name.  Looks for the template in the 
     * Mustache.TEMPLATES object.
     */
    Mustache.template = function(name) {
        var template = Mustache.TEMPLATES[name];
        return new CachedTemplate(template);
    };

})(Mustache);
