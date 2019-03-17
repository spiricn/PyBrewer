
pushd app

ng build \
    --base-href ./ \
    --prod \
    --output-path ../app_dist

popd

./push.sh

