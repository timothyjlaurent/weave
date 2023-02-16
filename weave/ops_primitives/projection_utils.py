import numpy as np
from .. import errors
import threading
import warnings

from sklearn.manifold import TSNE
from sklearn.decomposition import PCA

umap_lib = {}


def _get_umap():
    # Lazily load a cached version of UMAP - umap import
    # time is quite expensive so we want to do it once and
    # only when needed
    if "lib" not in umap_lib:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            import umap

            umap_lib["lib"] = umap
    return umap_lib["lib"]


def perform_2D_projection(
    np_array_of_embeddings: np.ndarray,
    projectionAlgorithm: str,
    algorithmOptions: dict,
) -> np.ndarray:
    if len(np_array_of_embeddings.shape) != 2:
        raise errors.WeaveInternalError(
            f"The input to the 2D projection must be a 2D array of embeddings, found {np_array_of_embeddings.shape}"
        )
    if projectionAlgorithm == "pca":
        projection = perform_2D_projection_pca(
            np_array_of_embeddings, algorithmOptions.get("pca", {})
        )
    elif projectionAlgorithm == "tsne":
        projection = perform_2D_projection_tsne(
            np_array_of_embeddings, algorithmOptions.get("tnse", {})
        )
    elif projectionAlgorithm == "umap":
        # Here, we are intentionally using PCA because UMAP is horribly slow
        # on even some basic cases and it is causing problems with Weave1 service.
        projection = perform_2D_projection_pca(
            np_array_of_embeddings, algorithmOptions.get("pca", {})
        )
        # projection = perform_2D_projection_umap(
        #     np_array_of_embeddings, algorithmOptions.get("umap", {})
        # )
    else:
        raise Exception("Unknown projection algorithm: " + projectionAlgorithm)
    return projection


def limit_embedding_dimensions(
    np_array_of_embeddings: np.ndarray, max_dimensions: int = 50
) -> np.ndarray:
    max_dimensions = min(max_dimensions, len(np_array_of_embeddings))
    if np_array_of_embeddings.shape[1] > max_dimensions:
        return PCA(n_components=max_dimensions).fit_transform(np_array_of_embeddings)
    return np_array_of_embeddings


def fit_subsample(np_array_of_embeddings: np.ndarray, size: int = 1500) -> np.ndarray:
    data_len = len(np_array_of_embeddings)
    if data_len <= size:
        return np_array_of_embeddings

    sample_ids = np.random.randint(data_len, size=size)
    return np_array_of_embeddings[sample_ids]


def perform_2D_projection_pca(
    np_array_of_embeddings: np.ndarray, options: dict
) -> np.ndarray:
    model = PCA(n_components=2)
    fit_data = fit_subsample(np_array_of_embeddings)
    model.fit(fit_data)
    return model.transform(np_array_of_embeddings)


def perform_2D_projection_tsne(
    np_array_of_embeddings: np.ndarray, options
) -> np.ndarray:
    n_samples = len(np_array_of_embeddings)
    return TSNE(
        n_components=2,
        perplexity=min(n_samples - 1, options.get("perplexity", 30)),
        n_iter=min(250, options.get("iterations", 250)),
        learning_rate=options.get("learningRate", "auto"),
        init="random",
    ).fit_transform(limit_embedding_dimensions(np_array_of_embeddings))


# TODO: we need lock stats in datadog
# UMAP is not thread safe, it crashes the server when called at the same
# time on parallel threads.
umap_lock = threading.Lock()


def perform_2D_projection_umap(
    np_array_of_embeddings: np.ndarray, options: dict
) -> np.ndarray:
    fit_data = fit_subsample(np_array_of_embeddings)
    n_samples = len(fit_data)
    model = _get_umap().UMAP(
        n_components=2,
        n_neighbors=min(n_samples - 1, options.get("neighbors", 15)),
        min_dist=options.get("minDist", 0.1),
        spread=options.get("spread", 1.0),
    )
    with umap_lock:
        model.fit(fit_data)
        return model.transform(np_array_of_embeddings)
