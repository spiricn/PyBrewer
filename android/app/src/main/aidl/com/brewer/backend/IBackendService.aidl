// IBackendService.aidl
package com.brewer.backend;

import com.brewer.backend.IBrewer;

// Declare any non-default types here with import statements

interface IBackendService {
    /**
     * Instantiates a brewer interface for given endpoint
     *
     * @param endpoint Brewer endpoint
     * @return Brewer instance on success, nul otherwise
     */
    IBrewer instantiate(String endpoint);
}
