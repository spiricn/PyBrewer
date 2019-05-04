package com.brewer.backend

/**
 * Hardware component
 */
data class Component(
    /**
     * Unique ID
     */
    val id : String,

    /**
     * Indication if the component should be graphed or not
     */
    val graph : Boolean,

    /**
     * Type of component
     */
    val componentType : String,

    /**
     * Human readable name
     */
    val name : String,

    /**
     * Component color
     */
    val color : String,

    /**
     * Component value
     */
    var value : Float
)